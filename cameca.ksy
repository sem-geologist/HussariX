meta:
  id: cameca
  file-extension:
    - qtiDat
    - imgDat
    - wdsDat
  endian: le

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
      - id: datasets
        type: dts
        
  dts:
    seq:
      - id: n_of_datasets
        type: u4
      - id: dataset
        type: dataset
        
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
      - id: header
        type: dataset_header
      - id: data
        type: data_common
        
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
      - id: body
        type:
          switch-on: element_res_src
          cases:
            'res_elem_src::wds': wds_dataset_header
            
            
  wds_dataset_header:
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
    # kudos to cameca for exposing those through drop-down menu :P
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
