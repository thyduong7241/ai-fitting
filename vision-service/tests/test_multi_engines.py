import pytest
from app.engines.registry import registry


def test_registered_engines_list():
    catalog = registry.list_engines()
    measurement_ids = [e.engine_id for e in catalog.measurement_engines]

    assert "hybrid_stereometry_2d" in measurement_ids
    assert "rtmpose_contour" in measurement_ids
    assert "shapy_3d" in measurement_ids

    shapy_meta = next(e for e in catalog.measurement_engines if e.engine_id == "shapy_3d")
    assert shapy_meta.requires_gpu is True


@pytest.mark.asyncio
async def test_dynamic_engine_switching():
    hybrid = registry.get_measurement_engine("hybrid_stereometry_2d")
    rtmpose = registry.get_measurement_engine("rtmpose_contour")
    shapy = registry.get_measurement_engine("shapy_3d")

    assert hybrid.engine_id == "hybrid_stereometry_2d"
    assert rtmpose.engine_id == "rtmpose_contour"
    assert shapy.engine_id == "shapy_3d"
