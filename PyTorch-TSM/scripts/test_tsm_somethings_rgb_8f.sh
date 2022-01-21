python test_models.py somethingv2 \
    --weights=pretrained/TSM_somethingv2_RGB_resnet50_shift8_blockres_avg_segment8_e45.pth \
    --test_segments=8 --batch_size=32 -j 24 --test_crops=1