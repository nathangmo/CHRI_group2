def convert_pos(*positions, window_size, window_scale):
        #invert x because of screen axes
        # 0---> +X
        # |
        # |
        # v +Y
        device_origin = (int(window_size[0]/2.0 + 0.038/2.0*window_scale),0)

        converted_positions = []
        for physics_pos in positions:
            x = device_origin[0]-physics_pos[0]*window_scale
            y = device_origin[1]+physics_pos[1]*window_scale
            converted_positions.append([x,y])
        if len(converted_positions)<=0:
            return None
        elif len(converted_positions)==1:
            return converted_positions[0]
        else:
            return converted_positions