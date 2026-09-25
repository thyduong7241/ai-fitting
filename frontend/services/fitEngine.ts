/**
 * Rule-based Fit Engine Service
 * Calculates fit scores and part evaluations matching OpenAPI 3.1 & Figma Design System
 */

import {
  Garment,
  GarmentSizeChart,
  UserProfile,
  FitPreference,
  SizeRecommendResponse,
  PartFitEvaluation,
  SizeComparisonItem,
  SizeLabel,
} from '@/types/fitting';

export function calculateFitRecommendation(
  garment: Garment,
  sizeCharts: GarmentSizeChart[],
  profile: UserProfile,
  preferenceOverride?: FitPreference
): SizeRecommendResponse {
  const pref = preferenceOverride || profile.fitPreference || 'regular';

  // Target ease based on preference (in cm)
  const targetEaseMap: Record<FitPreference, { min: number; ideal: number; max: number }> = {
    slim: { min: 0.5, ideal: 2.0, max: 4.0 },
    regular: { min: 3.0, ideal: 5.5, max: 8.0 },
    relaxed: { min: 7.0, ideal: 10.0, max: 14.0 },
  };

  const targetEase = targetEaseMap[pref];

  // Fabric stretch tolerance compensation
  const stretchBonusMap: Record<string, number> = {
    none: 0,
    low: 1.5,
    medium: 3.5,
    high: 6.0,
  };
  const stretchBonus = stretchBonusMap[garment.fabricStretch] || 0;

  const userShoulder = profile.shoulderCm || (profile.gender === 'male' ? 44 : 37);
  const userChest = profile.chestCm || (profile.gender === 'male' ? 94 : 84);
  const userWaist = profile.waistCm || (profile.gender === 'male' ? 78 : 65);
  const userHips = profile.hipsCm || (profile.gender === 'male' ? 96 : 90);

  const scoresBySize: Record<string, { score: number; evaluations: PartFitEvaluation[]; desc: string }> = {};

  sizeCharts.forEach((chart) => {
    const size = chart.size;

    // Evaluated diffs: Spec - Body
    const shoulderDiff = (chart.shoulderWidth ? chart.shoulderWidth - userShoulder : 2);
    const chestAvg = chart.chestMin && chart.chestMax ? (chart.chestMin + chart.chestMax) / 2 : (chart.chestMin || 88);
    const chestDiff = chestAvg - userChest + stretchBonus;

    const waistAvg = chart.waistMin && chart.waistMax ? (chart.waistMin + chart.waistMax) / 2 : (chart.waistMin || 70);
    const waistDiff = waistAvg - userWaist + stretchBonus;

    const hipsAvg = chart.hipsMin && chart.hipsMax ? (chart.hipsMin + chart.hipsMax) / 2 : (chart.hipsMin || 94);
    const hipsDiff = hipsAvg - userHips + stretchBonus;

    // Helper to evaluate part status
    function evaluatePart(
      part: 'shoulder' | 'chest' | 'waist' | 'hips' | 'length',
      partLabel: string,
      diff: number
    ): PartFitEvaluation {
      if (diff < -2) {
        return {
          part,
          partLabel,
          status: 'too_tight',
          statusLabel: `Quá chật (${diff.toFixed(1)}cm)`,
          diffCm: diff,
        };
      }
      if (diff < targetEase.min - 1) {
        return {
          part,
          partLabel,
          status: 'slightly_tight',
          statusLabel: `Ôm sát (${diff >= 0 ? '+' : ''}${diff.toFixed(1)}cm)`,
          diffCm: diff,
        };
      }
      if (diff <= targetEase.max + 1) {
        return {
          part,
          partLabel,
          status: 'perfect',
          statusLabel: `Vừa chuẩn (+${diff.toFixed(1)}cm cử động)`,
          diffCm: diff,
        };
      }
      if (diff <= targetEase.max + 5) {
        return {
          part,
          partLabel,
          status: 'slightly_loose',
          statusLabel: `Hơi rộng (+${diff.toFixed(1)}cm)`,
          diffCm: diff,
        };
      }
      return {
        part,
        partLabel,
        status: 'too_loose',
        statusLabel: `Quá rộng (+${diff.toFixed(1)}cm)`,
        diffCm: diff,
      };
    }

    const evalShoulder = evaluatePart('shoulder', 'Ngang vai', shoulderDiff);
    const evalChest = evaluatePart('chest', 'Vòng ngực', chestDiff);
    const evalWaist = evaluatePart('waist', 'Vòng eo', waistDiff);
    const evalHips = evaluatePart('hips', 'Vòng hông', hipsDiff);
    const evalLength: PartFitEvaluation = {
      part: 'length',
      partLabel: 'Chiều dài',
      status: 'perfect',
      statusLabel: 'Chuẩn dáng form',
      diffCm: 0,
    };

    // Calculate weighted score (0.0 - 1.0)
    const partScore = (evalObj: PartFitEvaluation) => {
      switch (evalObj.status) {
        case 'perfect': return 1.0;
        case 'slightly_tight': return 0.82;
        case 'slightly_loose': return 0.78;
        case 'too_tight': return 0.45;
        case 'too_loose': return 0.50;
      }
    };

    const weightedScore =
      partScore(evalShoulder) * 0.35 +
      partScore(evalChest) * 0.35 +
      partScore(evalWaist) * 0.15 +
      partScore(evalHips) * 0.10 +
      partScore(evalLength) * 0.05;

    let desc = '';
    if (weightedScore >= 0.90) {
      desc = 'Phom dáng suông đúng thiết kế, độ cử động hoàn hảo.';
    } else if (chestDiff < 0) {
      desc = `Ngực bị kích ${Math.abs(chestDiff).toFixed(1)}cm khi mặc thêm áo lót/áo len bên trong.`;
    } else if (shoulderDiff > 4) {
      desc = `Vai trễ ${shoulderDiff.toFixed(1)}cm so với khung vai của bạn.`;
    } else {
      desc = `Độ ôm tương đối, chênh lệch ${chestDiff.toFixed(1)}cm so với gu mặc thường ngày.`;
    }

    scoresBySize[size] = {
      score: Number(weightedScore.toFixed(2)),
      evaluations: [evalShoulder, evalChest, evalWaist, evalHips, evalLength],
      desc,
    };
  });

  // Pick best size
  const sortedSizes = Object.keys(scoresBySize).sort(
    (a, b) => scoresBySize[b].score - scoresBySize[a].score
  );

  const bestSize = (sortedSizes[0] || 'M') as SizeLabel;
  const bestResult = scoresBySize[bestSize] || {
    score: 0.95,
    evaluations: [],
    desc: 'Vừa vặn chuẩn xác.',
  };

  const prefLabelMap: Record<FitPreference, string> = {
    slim: 'Ôm nhẹ (Slim Fit)',
    regular: 'Vừa vặn (Regular Fit)',
    relaxed: 'Rộng rãi (Relaxed Fit)',
  };

  const sizeComparisons: Record<string, SizeComparisonItem> = {};
  Object.keys(scoresBySize).forEach((sz) => {
    const item = scoresBySize[sz];
    let badge = '● Khác';
    if (item.score >= 0.9) badge = '✓ Vừa vặn nhất';
    else if (item.evaluations[1]?.status === 'too_tight') badge = '● Quá chật';
    else if (item.evaluations[1]?.status === 'slightly_tight') badge = '● Hơi ôm';
    else if (item.evaluations[1]?.status === 'slightly_loose') badge = '● Hơi rộng';
    else badge = '● Quá rộng';

    sizeComparisons[sz] = {
      fitScore: item.score,
      badgeLabel: badge,
      description: item.desc,
    };
  });

  return {
    recommendedSize: bestSize,
    confidencePercent: Math.round(bestResult.score * 100),
    fitPreferenceLabel: prefLabelMap[pref],
    summaryExplanation: `Dựa trên chiều cao ${profile.heightCm}cm và số đo của ${profile.name}, Size ${bestSize} mang lại tỷ lệ vai và ngực chuẩn xác theo đúng gu ${prefLabelMap[pref].toLowerCase()}.`,
    breakdown: bestResult.evaluations,
    sizeComparisons,
  };
}
