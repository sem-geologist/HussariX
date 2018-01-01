meta:
  id: cameca
  file-extension:
    - qtiDat
    - imgDat
    - wdsDat
  endian: le
  license: GPL3

seq:
  - id: sxf_header
    type: sxf_head
  - id: sxf_data
    type: sxf_main

types:  
  sxf_main:
    seq:
      - id: version
        type: u4
      - id: global_options
        type: glob_opt
      - id: n_of_dataset
        type: u4
      - id: datasets
        type: dataset
        repeat: expr
        repeat-expr: n_of_dataset
        
  glob_opt:
    seq:
      - id: focus_freq
        type: u4
      - id: verify_xtal_after_flip
        type: u4
      - id: verify_xtal_before_start
        type: u4
      - id: bgnd_meas_every_nth
        type: u4
      - id: waiting_time
        type: u4
      
  dataset:
    seq:
      - id: dts_header
        type: dataset_header
      - id: dts_main
        type: data_common
        repeat: expr
        repeat-expr: dts_header.n_of_elements
      - id: comment
        type: c_hash_string
      - id: skip_unknown1
        size: 164
      - id: skip_unknown2 #TODO What is this
        size: 4
        if: dts_header.version == 0x12
      - id: dts_outer_metadata
        type: outer_metadata
      - id: skip_unknown3
        size: 52
      - id: outer_junk
        type:
          switch-on: _root.sxf_header.file_type
          cases:
            'file_type::image_mapping_result': outer_img_junk
        
  dataset_header:
    seq:
      - id: version
        type: u4
      - id: dataset_type
        type: u4
        enum: dataset_type
      - id: stage_x
        type: s4
      - id: stage_y
        type: s4
      - id: beam_x
        type: s4
      - id: beam_y
        type: s4
      - id: step_x
        type: f4
      - id: step_y
        type: f4
      - id: n_of_steps  # width
        type: u4
      - id: n_of_lines  # height
        type: u4
      - id: dataset_flags  # TODO
        type: s4
        repeat: expr
        repeat-expr: 6
      - id: stage_z
        type: u4
        repeat: expr
        repeat-expr: 49
      - id: flags2  # TODO
        type: s4
        repeat: expr
        repeat-expr: 10
      - id: setup_file_name
        type: c_hash_string
      - id: n_of_elements
        type: u4

  data_common:
    seq:
      - id: version
        type: u4
      - id: element_res_src
        type: u4
        enum: res_elem_src
      - id: signal_header
        size: 68
        type:
          switch-on: element_res_src
          cases:
            'res_elem_src::video': video_signal_header
            'res_elem_src::camera': empty_signal_header
            _: xray_signal_header
      - id: unknown_flag
        type: u4
      - id: unknown_stuff
        size: 12
      - id: n_of_undefined_blocks
        type: u4
      - id: undefined_blocks
        size: 12
        repeat: expr
        repeat-expr: n_of_undefined_blocks
      - id: signal
        type:
          switch-on: _root.sxf_header.file_type
          cases:
            'file_type::image_mapping_result': image_section_data
            'file_type::wds_results': wds_scan_data
        
  xray_signal_header:
    seq:
      - id: atom_number
        type: u4
      - id: x_ray_line
        type: u4
      - id: order
        type: u4
      - id: spect_no
        type: u4
      - id: xtal4
        type: str
        size: 4
        encoding: ASCII
      - id: two_d
        type: f4
      - id: k
        type: f4
      - id: unkwn4
        size: 4
      - id: hv
        type: f4
      - id: current
        type: f4
      - id: peak_pos
        type: u4
      - id: bias
        type: u4
      - id: gain
        type: u4
      - id: dtime
        type: u4
      - id: blin
        type: u4
      - id: window
        type: u4
      - id: mode
        type: u4
        enum: pha_mode
  
  empty_signal_header:
    seq:
      - id: dummy
        size: 68
      
  video_signal_header:
    seq:
      - id: channel
        type: u4
      - id: signal
        type: u4
        enum: mach_signal_type
      - id: padding
        size: 24
      - id: hv
        type: f4
      - id: current
        type: f4
      - id: padding2
        size: 28
        
  image_section_data:
    seq:
      - id: struct_v
        type: u4
      - id: definition_node
        type: u4
        enum: dataset_type
      - id: stage_x
        type: s4
      - id: stage_y
        type: s4
      - id: beam_x
        type: s4
      - id: beam_y
        type: s4
      - id: step_x
        type: f4
      - id: step_y
        type: f4
      - id: width  # width
        type: u4
      - id: height  # height
        type: u4
      - id: z_axis
        type: u4
      - id: img_cameca_dtype
        type: u4
        enum: image_array_dtype
      - id: dwell_time
        type: f4
      - id: accumulation_n
        type: u4
        if: '(definition_node != dataset_type::line_stage) and (definition_node != dataset_type::line_beam)'
      - id: unkn_flag
        type: u4
      - id: data_size
        type: u4
      - id: unkn_flag2
        type: u4
        if: '(definition_node != dataset_type::line_stage) and (definition_node != dataset_type::line_beam)'
      - id: unkn_flag3
        type: u4
        if: '(definition_node != dataset_type::line_stage) and (definition_node != dataset_type::line_beam)'
      - id: unkn_flag4
        type: f4
        if: '(definition_node != dataset_type::line_stage) and (definition_node != dataset_type::line_beam)'
      - id: data
        size: '(definition_node != dataset_type::line_stage) and (definition_node != dataset_type::line_beam) ? data_size - 12 : data_size'
      - id: unknown2
        size: 56
      - id: lut_name
        type: c_hash_string
      - id: signal_name
        type: c_hash_string
      - id: unknown3
        size: 52
      - id: img_rotation
        type: f4
      - id: unknown4
        size: 8
        
  wds_scan_data:
    seq:
      - id: version
        type: u4
      - id: wds_start_pos
        type: u4
      - id: steps
        type: u4
      - id: step_size
        type: f4
      - id: dwell_time
        type: f4
      - id: beam_size #TODO is it?
        type: u4
      - id: data_array_size
        type: u4
      - id: data
        size: data_array_size
      - id: unknown_flag
        type: u4
      - id: signal_name
        type: c_hash_string
      - id: unknow_sector
        size: 104
      - id: n_of_annot_lines
        type: u4
      - id: annot_lines_table
        type: annotated_lines
        repeat: expr
        repeat-expr: n_of_annot_lines
      - id: unknonw_sector2
        size: 8
  
  annotated_lines:
    seq:
      - id: element
        type: u4
      - id: line
        type: u4
      - id: order
        type: u4
      - id: reserverd1
        type: u4
      - id: reserverd2
        type: u4
  
  cs_data:
    seq:
      - id: unkn_flag_sect
        type: u4
      - id: data_size
        type: u4
      - id: data
        size: data_size
  
  image_data:
    seq:
      - id: accumulation_n
        type: u4
      - id: unkn_flag_img
        type: u4
      - id: data_size
        type: u4
      - id: unkn_flag_img2
        type: u4
      - id: unkn_flag_img3
        type: u4
      - id: unkn_flag_img4
        type: f4
      - id: data
        size: data_size - 12
       
  sxf_head:
    seq:
      - id: file_type
        type: u1
        enum: file_type
      - id: magic
        size: 3
        contents: fxs
      - id: sxf_version
        type: u4
      - id: comment
        type: c_hash_string
      - id: unknown
        size: 0x1C
      - id: file_changes
        type: changes
      - id: unkn_v4
        size: 8
        if: sxf_version >= 4
  
  outer_metadata:
    seq:
      - id: version
        type: u4
      - id: datetime
        type: u8
        doc: 'MS FILETIME'
      - id: x_axis
        type: s4
      - id: y_axis
        type: s4
      - id: z_axis
        type: s4
      - id: unknown1
        size: 76
      - id: unknown2
        size: 24
        if: version == 6
        
  outer_img_junk: #it is probably Dynamic TODO
    seq:
      - id: additional_junk
        size: 28
      - id: thingy
        type: c_hash_string
      - id: additional_junk2
        size: 309
        
        
  c_hash_string:
    seq:
      - id: str_len
        type: u4
      - id: text
        type: str
        size: str_len
        encoding: ASCII
  
  changes:
    seq:
      - id: n_of_changes
        type: u4
      - id: changes
        type: change
        repeat: expr
        repeat-expr: n_of_changes
        
  change:
    seq:
      - id: filetime
        type: u8
      - id: change
        type: c_hash_string
        
enums:
  file_type:
    1: wds_setup
    2: image_mapping_setup
    3: calibration_setup
    4: quanti_setup
    # what is 5?
    6: wds_results
    7: image_mapping_result
    8: calibration_result
    9: quanti_result
    10: overlap_table

  dataset_type:
    0: point
    1: line_stage
    2: line_beam
    3: grid_stage
    4: grid_beam
    5: polygon_masked_stage_raster
    6: polygon_masked_beam_raster
    7: free_points
    
  res_elem_src:
    # kudos to cameca butterfingers
    # for exposing those in GUI as drop-down menu :P
    0: undefined
    1: wds
    2: eds
    3: video
    4: other
    5: qti_diff
    6: qti_stoch
    7: qti_matrix
    8: imove
    9: imphcl
    10: im_phid
    11: imqti_wds_bkgd_meas
    12: imqti_wds_bkgd_computed
    13: imqti_wt
    14: imqti_at
    15: imqti_sum
    16: imqti_age
    17: imqti_oxy
    18: imxon_video
    19: camera
    20: wds_computed
    21: eds_bkgd
  
  pha_mode:
    0: integral
    1: manual
    2: semi_manual
    
  mach_signal_type:
    0: se
    1: fara
    2: bse  # 0x02 as BSE is on SX100, but not on SXFive
    3: abs
    # 4?
    5: cl
    0x3F000002: bse_z  # BSE Z on SxFive
    0x38070002: bse_t  # all signal types with lowest bits as 0x02 are BSE?
    0x30000002: bse_1
    0x18000002: bse_2
    0x06000002: bse_3
    0x03000002: bse_4
    0x0C000002: bse_5
  
  image_array_dtype:
    0: uint8
    #what is 1-6?
    7: float32
    8: rgbx
