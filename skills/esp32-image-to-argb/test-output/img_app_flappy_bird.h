#ifndef IMG_IMG_APP_FLAPPY_BIRD_H
#define IMG_IMG_APP_FLAPPY_BIRD_H

/* LVGL image header for 'img_app_flappy_bird' — do not modify by hand */

#ifdef __has_include
    #if __has_include("lvgl.h")
        #ifndef LV_LVGL_H_INCLUDE_SIMPLE
            #define LV_LVGL_H_INCLUDE_SIMPLE
        #endif
    #endif
#endif

#if defined(LV_LVGL_H_INCLUDE_SIMPLE)
    #include "lvgl.h"
#else
    #include "lvgl/lvgl.h"
#endif

#ifndef LV_ATTRIBUTE_MEM_ALIGN
#define LV_ATTRIBUTE_MEM_ALIGN
#endif

#ifndef LV_ATTRIBUTE_IMAGE_IMG_APP_FLAPPY_BIRD
#define LV_ATTRIBUTE_IMAGE_IMG_APP_FLAPPY_BIRD
#endif

extern const LV_ATTRIBUTE_MEM_ALIGN LV_ATTRIBUTE_LARGE_CONST
    LV_ATTRIBUTE_IMAGE_IMG_APP_FLAPPY_BIRD uint8_t img_app_flappy_bird_map[];

extern const lv_image_dsc_t img_app_flappy_bird;

#endif /* IMG_IMG_APP_FLAPPY_BIRD_H */
