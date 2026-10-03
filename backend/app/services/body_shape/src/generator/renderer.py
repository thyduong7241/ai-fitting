"""Render 2D body illustration into clean PNG images using Pillow."""

from PIL import Image, ImageDraw
from typing import Tuple, Optional
from ..body_model.parameters import BodyParameters
from .geometry import (
    generate_torso_contour,
    generate_leg_contour,
    generate_arm_contour
)


class BodyRenderer:
    def __init__(
        self,
        image_size: Tuple[int, int] = (600, 1000),
        bg_color: Tuple[int, int, int] = (248, 249, 250),
        body_color: Tuple[int, int, int] = (215, 222, 230),
        outline_color: Tuple[int, int, int] = (90, 105, 120),
        outline_width: int = 2,
        seed: Optional[int] = 42
    ):
        self.width, self.height = image_size
        self.bg_color = bg_color
        self.body_color = body_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.seed = seed

    def render(self, params: BodyParameters, height_cm: float = 165.0, reference_height_cm: Optional[float] = None) -> Image.Image:
        """
        Render full-body 2D avatar illustration from normalized parameters.
        Uses 2x supersampling for crisp, anti-aliased contours.
        If reference_height_cm is provided, height scales proportionally to reference.
        """
        scale_factor = 2
        w_hi = self.width * scale_factor
        h_hi = self.height * scale_factor

        img = Image.new("RGB", (w_hi, h_hi), self.bg_color)
        draw = ImageDraw.Draw(img)

        # Baseline body occupies ~88% of vertical canvas height
        base_body_h = h_hi * 0.88
        if reference_height_cm and reference_height_cm > 0:
            total_body_h = base_body_h * (height_cm / reference_height_cm)
        else:
            total_body_h = base_body_h

        # Align body vertically from bottom feet level so height variation shows at head
        bottom_y = h_hi * 0.94
        top_y = bottom_y - total_body_h
        center_x = w_hi * 0.5

        # Layer 1: Arms (behind or beside torso)
        left_arm = generate_arm_contour(params, center_x, top_y, total_body_h, side="left")
        right_arm = generate_arm_contour(params, center_x, top_y, total_body_h, side="right")

        # Layer 2: Legs
        left_leg = generate_leg_contour(params, center_x, top_y, total_body_h, side="left")
        right_leg = generate_leg_contour(params, center_x, top_y, total_body_h, side="right")

        # Layer 3: Head & Torso
        torso = generate_torso_contour(params, center_x, top_y, total_body_h)

        # Draw parts in layered order
        # Arms
        for arm in [left_arm, right_arm]:
            draw.polygon(arm, fill=self.body_color, outline=self.outline_color, width=self.outline_width * scale_factor)

        # Legs
        for leg in [left_leg, right_leg]:
            draw.polygon(leg, fill=self.body_color, outline=self.outline_color, width=self.outline_width * scale_factor)

        # Torso & Head
        draw.polygon(torso, fill=self.body_color, outline=self.outline_color, width=self.outline_width * scale_factor)

        # Downsample back to target resolution for smooth anti-aliased edges
        final_img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        return final_img
