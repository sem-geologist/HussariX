# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Cameca(KaitaiStruct):
    """This parser is created for reading the proprietary binary data formats
    produced with Cameca Peaksight software for EPMA.
    
    DISCLAIMERS
    This reverse engineering based implementation is granted by Petras Jokubauskas
    (klavishas@gmail.com; p.jokubauskas@uw.edu.pl).
    Author of this implementation is not affiliated with the Cameca or Ametek inc.
    Words, which by some parts could be recognized to be a trademark,
    are used in this file only for informative documentation of the code and
    it is not used for self-advertisement or criticism of rightful trademark holders.
    This reverse engineering pursuit is aimed for interoperability and
    such right is protected by EU directive 2009/24/EC.
    
    This RE-based implementation of formats is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    Lesser General Public License for more details.
    """

    class MatrixCorrectionType(Enum):
        pap = 0
        xphi = 1

    class DatasetType(Enum):
        point = 0
        line_stage = 1
        line_beam = 2
        grid_stage = 3
        grid_beam = 4
        polygon_masked_stage_raster = 5
        polygon_masked_beam_raster = 6
        free_points = 7

    class PhaMode(Enum):
        integral = 0
        differential = 1
        differential_auto = 2

    class SubcountingMode(Enum):
        none = 0
        subcounting_p_b_p_b = 1
        subcounting_p_p_b_b = 2
        time_0_intercept = 3
        decontamination_auto_test = 4
        chi_square_test = 5
        sub_chi_p_b_p_b = 6
        sub_chi_p_p_b_b = 7

    class WdsScanType(Enum):
        full = 0
        relative = 1
        absolute = 2

    class QuantiMode(Enum):
        area = 0
        peak_background = 1

    class MSpectSameLineHandling(Enum):
        average = 0
        sum = 1

    class PolygonSelectionMode(Enum):
        none = 0
        on_image_positions = 1
        stage_positions = 2

    class BackgroundType(Enum):
        linear = 1
        exponential = 2

    class VideoSignalType(Enum):
        se = 0
        fara = 1
        bse = 2
        abs = 3
        cl = 5
        bse_4 = 50331650
        bse_3 = 100663298
        bse_5 = 201326594
        bse_2 = 402653186
        bse_1 = 805306370
        bse_t = 939982850
        bse_z = 1056964610

    class XrayLine(Enum):
        kb = 1
        ka = 2
        lg4 = 3
        lg3 = 4
        lg2 = 5
        lg1 = 6
        lb9 = 7
        lb10 = 8
        lb7 = 9
        lb2 = 10
        lb6 = 11
        lb3 = 12
        lb4 = 13
        lb = 14
        la = 15
        lv = 16
        ll = 17
        mg = 18
        mb = 19
        ma = 20
        mz = 21
        mz2 = 22
        m1n2 = 23
        m1n3 = 24
        m2n1 = 25
        m2n4 = 26
        m2o4 = 27
        m3n1 = 28
        m3n4 = 29
        m3o1 = 30
        m3o4 = 31
        m4o2 = 32
        ska1 = 100
        ska2 = 101
        ska3 = 102
        ska4 = 103
        ska5 = 104
        ska6 = 105
        skb1 = 106

    class FileType(Enum):
        wds_setup = 1
        image_mapping_setup = 2
        calibration_setup = 3
        quanti_setup = 4
        wds_results = 6
        image_mapping_results = 7
        calibration_results = 8
        quanti_results = 9
        overlap_table = 10

    class AnalysisMode(Enum):
        all = 0
        by_stochiometry = 1
        by_difference = 2
        stoch_and_difference = 3
        with_matrix_definition = 4
        matrix_def_and_stoch = 7

    class SignalSource(Enum):
        undefined = 0
        wds = 1
        eds = 2
        video = 3
        other = 4
        qti_diff = 5
        qti_stoch = 6
        qti_matrix = 7
        im_ove = 8
        im_phcl = 9
        im_phid = 10
        im_qti_wds_bkgd_meas = 11
        im_qti_wds_bkgd_computed = 12
        im_qti_wt = 13
        im_qti_at = 14
        im_qti_sum = 15
        im_qti_age = 16
        im_qti_oxy = 17
        im_xon_video = 18
        im_camera = 19
        wds_computed = 20
        im_qti_eds_back_meas = 21

    class DatasetExtrasType(Enum):
        wds_and_cal_footer = 2
        qti_v5_footer = 4
        img_sec_footer = 5
        qti_v6_footer = 6

    class ImageArrayDtype(Enum):
        uint8 = 0
        float32 = 7
        rgbx = 8
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header = Cameca.SxfHeader(self._io, self, self._root)
        _on = self.header.file_type
        if _on == Cameca.FileType.calibration_results:
            self.content = Cameca.SxfMain(self._io, self, self._root)
        elif _on == Cameca.FileType.image_mapping_setup:
            self.content = Cameca.ImgSetup(self._io, self, self._root)
        elif _on == Cameca.FileType.image_mapping_results:
            self.content = Cameca.SxfMain(self._io, self, self._root)
        elif _on == Cameca.FileType.wds_results:
            self.content = Cameca.SxfMain(self._io, self, self._root)
        elif _on == Cameca.FileType.wds_setup:
            self.content = Cameca.WdsSetup(self._io, self, self._root)
        elif _on == Cameca.FileType.quanti_results:
            self.content = Cameca.SxfMain(self._io, self, self._root)
        elif _on == Cameca.FileType.quanti_setup:
            self.content = Cameca.QtiSetup(self._io, self, self._root)
        elif _on == Cameca.FileType.overlap_table:
            self.content = Cameca.OverlapCorrectionsContent(self._io, self, self._root)
        elif _on == Cameca.FileType.calibration_setup:
            self.content = Cameca.CalSetup(self._io, self, self._root)

    class DtsWdsCalibFooter(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if self._root.header.file_type == Cameca.FileType.calibration_results:
                self.reserved_0 = self._io.read_bytes(4)

            if self._root.header.file_type == Cameca.FileType.calibration_results:
                self.num_datetime_and_pos = self._io.read_u4le()

            self.datetime_and_pos = []
            for i in range((self.num_datetime_and_pos if self._root.header.file_type == Cameca.FileType.calibration_results else 1)):
                self.datetime_and_pos.append(Cameca.SpaceTime(self._io, self, self._root))

            self.reserved_1 = self._io.read_bytes(4)
            if self._root.header.file_type.value != 8:
                self.reserved_wds_ending_1 = self._io.read_bytes(4)

            if self._root.header.file_type.value != 8:
                self.dataset_is_selected = self._io.read_u4le()

            if self._root.header.file_type.value != 8:
                self.reserved_wds_ending_2 = self._io.read_bytes(40)

            if self._root.header.file_type.value == 8:
                self.standard = Cameca.StandardCompositionTable(self._io, self, self._root)



    class XraySignalHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element = Cameca.ElementT(self._io, self, self._root)
            self.xray_line = KaitaiStream.resolve_enum(Cameca.XrayLine, self._io.read_u4le())
            self.order = self._io.read_u4le()
            self.spect_no = self._io.read_u4le()
            self._raw_xtal = self._io.read_bytes(4)
            _io__raw_xtal = KaitaiStream(BytesIO(self._raw_xtal))
            self.xtal = Cameca.XtalT(_io__raw_xtal, self, self._root)
            self.two_d = self._io.read_f4le()
            self.k = self._io.read_f4le()
            self.reserved_0 = self._io.read_bytes(4)
            self.hv = self._io.read_f4le()
            self.beam_current = self._io.read_f4le()
            self.peak_pos = self._io.read_u4le()
            self.counter_setting = Cameca.CounterSetting(self._io, self, self._root)

        @property
        def combi_string(self):
            if hasattr(self, '_m_combi_string'):
                return self._m_combi_string

            if self._parent.signal_type == Cameca.SignalSource.wds:
                self._m_combi_string = str(self.spect_no) + u": " + self.xtal.full_name

            return getattr(self, '_m_combi_string', None)


    class PolygonPoint(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()


    class SubSetup(KaitaiStruct):
        """this is a rought reverse engineared and far from complete."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.reserved_0 = self._io.read_bytes(4)
            self.condition_name = Cameca.CSharpString(self._io, self, self._root)
            self.reserved_1 = self._io.read_bytes(20)
            self.heat = self._io.read_u4le()
            self.hv = self._io.read_u4le()
            self.i_emission = self._io.read_u4le()
            self.xhi = self._io.read_s4le()
            self.yhi = self._io.read_s4le()
            self.xlo = self._io.read_s4le()
            self.ylo = self._io.read_s4le()
            self.aperture_x = self._io.read_s4le()
            self.aperture_y = self._io.read_s4le()
            self.c1 = self._io.read_u4le()
            self.c2 = self._io.read_u4le()
            self.reserved_2 = self._io.read_bytes(4)
            self.current_set = self._io.read_s4le()
            self.beam_focus = self._io.read_s4le()
            self.reserved_3 = self._io.read_s4le()
            self.reserved_4 = self._io.read_s4le()
            self.beam_focus_2 = self._io.read_s4le()
            self.beam_size = self._io.read_s4le()
            self.stigmator_amplitude = self._io.read_s4le()
            self.stigmator_angle = self._io.read_s4le()
            self.reserved_flags_5 = []
            for i in range(6):
                self.reserved_flags_5.append(self._io.read_s4le())

            self.extractor = self._io.read_s4le()
            self.suppressor = self._io.read_s4le()
            self.reserved_flags_6 = []
            for i in range((86 if self._root.header.file_type.value > 1 else 85)):
                self.reserved_flags_6.append(self._io.read_s4le())

            if self._root.header.file_type.value > 1:
                self.num_eds_meas_setups = self._io.read_u4le()

            if self._root.header.file_type.value > 1:
                self.eds_measurement_setups = []
                for i in range(self.num_eds_meas_setups):
                    self.eds_measurement_setups.append(Cameca.QtiEdsMeasurementSetup(self._io, self, self._root))


            self.default_eds_live_time = self._io.read_f4le()
            self.not_re_flag_5 = self._io.read_u4le()
            self.eds_roi_fwhm = self._io.read_f4le()
            self.reserved_flags_7 = self._io.read_bytes(8)
            if self._root.header.file_type.value > 1:
                self.wds_measurement_struct_type = self._io.read_u4le()

            if self.wds_measurement_struct_type == 3:
                self.wds_img_spect_setups = Cameca.ImgWdsSpectSetups(self._io, self, self._root)

            if self.wds_measurement_struct_type >= 19:
                self.wds_qti_measurement_setups = Cameca.QtiWdsMeasurementSetups(self._io, self, self._root)



    class CalibSignal(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.len_data = self._io.read_u4le()
            self.unkn_x = self._io.read_bytes(4)
            self.total_size = self._io.read_u4le()
            self._raw_data = []
            self.data = []
            for i in range(self.total_size // self.len_data):
                self._raw_data.append(self._io.read_bytes(self.len_data))
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data[i]))
                self.data.append(Cameca.CalibItem(_io__raw_data, self, self._root))

            self.calib_peak_time = self._io.read_f4le()
            self.calib_bkgd_time = self._io.read_f4le()
            self.bkgd_1_pos = self._io.read_s4le()
            self.bkgd_2_pos = self._io.read_s4le()
            self.bkgd_slope = self._io.read_f4le()
            self.quanti_mode = KaitaiStream.resolve_enum(Cameca.QuantiMode, self._io.read_u4le())
            self.pk_area_range = self._io.read_u4le()
            self.pk_area_channels = self._io.read_u4le()
            self.pk_area_bkgd_1 = self._io.read_s4le()
            self.pk_area_bkgd_2 = self._io.read_s4le()
            self.pk_area_n_accumulation = self._io.read_u4le()
            self.not_re_area_flags = self._io.read_bytes(24)
            self.num_pk_area_wds_spectra = self._io.read_u4le()
            self.pk_area_wds_spectra = []
            for i in range(self.num_pk_area_wds_spectra):
                self.pk_area_wds_spectra.append(Cameca.QuantiWdsScan(self._io, self, self._root))



    class WdsItemExtraEnding(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.item_comment = Cameca.CSharpString(self._io, self, self._root)
            self.not_re_flag_0 = self._io.read_f4le()
            self.not_re_flag_1 = self._io.read_s4le()
            self.not_re_flag_2 = self._io.read_s4le()
            self.color = self._io.read_bytes(4)
            self.not_re_flag_3 = self._io.read_f4le()
            self.not_re_flag_4 = self._io.read_f4le()
            self.not_re_falg_5 = self._io.read_bytes(16)


    class WdsScanSpectSetup(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_xtal = self._io.read_bytes(4)
            _io__raw_xtal = KaitaiStream(BytesIO(self._raw_xtal))
            self.xtal = Cameca.XtalT(_io__raw_xtal, self, self._root)
            self.two_d = self._io.read_f4le()
            self.k = self._io.read_f4le()
            self.wds_scan_type = KaitaiStream.resolve_enum(Cameca.WdsScanType, self._io.read_u4le())
            self.min_pos = self._io.read_u4le()
            self.reserved_1 = self._io.read_u4le()
            self.reserved_2 = self._io.read_u4le()
            self.reserved_3 = self._io.read_u4le()
            self.max_pos = self._io.read_u4le()
            self.reserved_4 = self._io.read_bytes((4 * 3))
            self.position = self._io.read_u4le()
            self.element = Cameca.ElementT(self._io, self, self._root)
            self.xray_line = KaitaiStream.resolve_enum(Cameca.XrayLine, self._io.read_u4le())
            self.order = self._io.read_u4le()
            self.offset_1 = self._io.read_s4le()
            self.offset_2 = self._io.read_s4le()
            self.counter_setting = Cameca.CounterSetting(self._io, self, self._root)


    class DatasetItem(KaitaiStruct):
        def __init__(self, n_points, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.n_points = n_points
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.signal_type = KaitaiStream.resolve_enum(Cameca.SignalSource, self._io.read_u4le())
            _on = self.signal_type
            if _on == Cameca.SignalSource.qti_stoch:
                self._raw_signal_header = self._io.read_bytes(68)
                _io__raw_signal_header = KaitaiStream(BytesIO(self._raw_signal_header))
                self.signal_header = Cameca.LimitedSignalHeader(_io__raw_signal_header, self, self._root)
            elif _on == Cameca.SignalSource.qti_diff:
                self._raw_signal_header = self._io.read_bytes(68)
                _io__raw_signal_header = KaitaiStream(BytesIO(self._raw_signal_header))
                self.signal_header = Cameca.LimitedSignalHeader(_io__raw_signal_header, self, self._root)
            elif _on == Cameca.SignalSource.qti_matrix:
                self._raw_signal_header = self._io.read_bytes(68)
                _io__raw_signal_header = KaitaiStream(BytesIO(self._raw_signal_header))
                self.signal_header = Cameca.LimitedSignalHeader(_io__raw_signal_header, self, self._root)
            elif _on == Cameca.SignalSource.im_camera:
                self._raw_signal_header = self._io.read_bytes(68)
                _io__raw_signal_header = KaitaiStream(BytesIO(self._raw_signal_header))
                self.signal_header = Cameca.EmptySignalHeader(_io__raw_signal_header, self, self._root)
            elif _on == Cameca.SignalSource.video:
                self._raw_signal_header = self._io.read_bytes(68)
                _io__raw_signal_header = KaitaiStream(BytesIO(self._raw_signal_header))
                self.signal_header = Cameca.VideoSignalHeader(_io__raw_signal_header, self, self._root)
            else:
                self._raw_signal_header = self._io.read_bytes(68)
                _io__raw_signal_header = KaitaiStream(BytesIO(self._raw_signal_header))
                self.signal_header = Cameca.XraySignalHeader(_io__raw_signal_header, self, self._root)
            self.not_re_flag = self._io.read_u4le()
            if self.version >= 3:
                self.reserved_0 = self._io.read_bytes(12)

            if self.version >= 3:
                self.num_reserved_1 = self._io.read_u4le()

            if self.version >= 3:
                self.reserved_1 = []
                for i in range(self.num_reserved_1):
                    self.reserved_1.append(self._io.read_bytes(12))


            _on = self._root.header.file_type
            if _on == Cameca.FileType.image_mapping_results:
                self.signal = Cameca.ImageProfileSignal(self._io, self, self._root)
            elif _on == Cameca.FileType.wds_results:
                self.signal = Cameca.WdsScanSignal(self._io, self, self._root)
            elif _on == Cameca.FileType.quanti_results:
                self.signal = Cameca.WdsQtiSignal(self.n_points, self._io, self, self._root)
            elif _on == Cameca.FileType.calibration_results:
                self.signal = Cameca.CalibSignal(self._io, self, self._root)


    class ElementT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.atomic_number = self._io.read_u4le()


    class CounterSetting(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bias = self._io.read_u4le()
            self.gain = self._io.read_u4le()
            self.dead_time = self._io.read_u4le()
            self.base_line = self._io.read_u4le()
            self.window = self._io.read_u4le()
            self.mode = KaitaiStream.resolve_enum(Cameca.PhaMode, self._io.read_u4le())


    class DtsImgSecFooter(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.datetime_and_pos = Cameca.SpaceTime(self._io, self, self._root)
            self.reserved_0 = self._io.read_bytes(4)
            self.reserved_1 = self._io.read_bytes(8)
            self.reserved_2 = self._io.read_bytes(64)
            self.num_subsections = self._io.read_u4le()
            self.subsections = []
            for i in range(self.num_subsections):
                self.subsections.append(Cameca.ImgFooterSubsection(self._io, self, self._root))



    class ImgWdsSpectSetups(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.wds_img_spect_setup_table = []
            for i in range(5):
                self.wds_img_spect_setup_table.append(Cameca.ImgWdsSpectSetup(self._io, self, self._root))



    class ColorBarTicks(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_colorbar_ticks = self._io.read_u4le()
            self.colorbar_ticks = []
            for i in range(self.num_colorbar_ticks):
                self.colorbar_ticks.append(Cameca.ColorTick(self._io, self, self._root))

            if self.num_colorbar_ticks > 0:
                self.max_value = self._io.read_f4le()

            self.reserved_0 = self._io.read_f4le()
            self.reserved_1 = self._io.read_bytes(4)
            self.num_custom_colorbar_labels = self._io.read_u4le()
            self.custom_colorbar_labels = []
            for i in range(self.num_custom_colorbar_labels):
                self.custom_colorbar_labels.append(Cameca.BarLabel(self._io, self, self._root))



    class ImageProfileSignal(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.dataset_type = KaitaiStream.resolve_enum(Cameca.DatasetType, self._io.read_u4le())
            self.stage_x = self._io.read_s4le()
            self.stage_y = self._io.read_s4le()
            self.beam_x = self._io.read_f4le()
            self.beam_y = self._io.read_f4le()
            self.step_x = self._io.read_f4le()
            self.step_y = self._io.read_f4le()
            self.width = self._io.read_u4le()
            self.height = self._io.read_u4le()
            self.z_axis = self._io.read_s4le()
            self.img_pixel_dtype = KaitaiStream.resolve_enum(Cameca.ImageArrayDtype, self._io.read_u4le())
            self.dwell_time = self._io.read_f4le()
            if  ((self.dataset_type != Cameca.DatasetType.line_stage) and (self.dataset_type != Cameca.DatasetType.line_beam)) :
                self.n_frames = self._io.read_u4le()

            self.not_re_flag = self._io.read_u4le()
            self.data_size = self._io.read_u4le()
            if  ((self.dataset_type != Cameca.DatasetType.line_stage) and (self.dataset_type != Cameca.DatasetType.line_beam)) :
                self.not_re_flag2 = self._io.read_u4le()

            if  ((self.dataset_type != Cameca.DatasetType.line_stage) and (self.dataset_type != Cameca.DatasetType.line_beam)) :
                self.not_re_flag3 = self._io.read_f4le()

            if  ((self.dataset_type != Cameca.DatasetType.line_stage) and (self.dataset_type != Cameca.DatasetType.line_beam)) :
                self.not_re_flag4 = self._io.read_f4le()

            self.data = []
            for i in range(self.num_data):
                self.data.append(Cameca.LazyData(self._root._io.pos(), self.frame_size, self._io, self, self._root))

            self.reserved_0 = self._io.read_bytes(56)
            self.lut_name = Cameca.CSharpString(self._io, self, self._root)
            self.signal_name = Cameca.CSharpString(self._io, self, self._root)
            self.intensity_min = self._io.read_f4le()
            self.intensity_max = self._io.read_f4le()
            self.reserved_1 = self._io.read_bytes(20)
            self.visible_width = self._io.read_u4le()
            self.visible_height = self._io.read_u4le()
            self.colorbar_ticks = Cameca.ColorBarTicks(self._io, self, self._root)
            self.img_rotation = self._io.read_f4le()
            self.reserved_2 = self._io.read_bytes(8)
            if self.version >= 6:
                self.reserved_v6 = self._io.read_bytes(12)


        @property
        def array_data_size(self):
            if hasattr(self, '_m_array_data_size'):
                return self._m_array_data_size

            self._m_array_data_size = (self.data_size - (0 if  ((self.dataset_type == Cameca.DatasetType.line_stage) or (self.dataset_type == Cameca.DatasetType.line_beam))  else 12))
            return getattr(self, '_m_array_data_size', None)

        @property
        def frame_size(self):
            if hasattr(self, '_m_frame_size'):
                return self._m_frame_size

            self._m_frame_size = (((1 if self.img_pixel_dtype.value == 0 else 4) * self.height) * self.width)
            return getattr(self, '_m_frame_size', None)

        @property
        def num_data(self):
            if hasattr(self, '_m_num_data'):
                return self._m_num_data

            self._m_num_data = (self.array_data_size // self.frame_size if self.frame_size != 0 else 0)
            return getattr(self, '_m_num_data', None)


    class ModificationAttributes(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.action = (self._io.read_bytes_term(3, False, True, True)).decode(u"CP1252")
            self.description = (self._io.read_bytes_term(3, False, True, False)).decode(u"CP1252")
            self.user_comment = (self._io.read_bytes_full()).decode(u"CP1252")


    class OffsetPos(KaitaiStruct):
        """type for file offset position for eventual in-place edditing of values
        externally.
        """
        def __init__(self, pos, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.pos = pos
            self._read()

        def _read(self):
            pass


    class LazyData(KaitaiStruct):
        """its _read method needs to be reimplemented in target language
        to seek in the stream by provided size by parameter instead
        of reading into memory
        """
        def __init__(self, offset, len_bytes, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.offset = offset
            self.len_bytes = len_bytes
            self._read()

        def _read(self):
            self.bytes = self._io.read_bytes(self.len_bytes)


    class QtiDataItem(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.beam_current = self._io.read_f4le()
            self.peak_cps = self._io.read_f4le()
            self.peak_time = self._io.read_f4le()
            self._raw_ofs_bkgd = self._io.read_bytes(0)
            _io__raw_ofs_bkgd = KaitaiStream(BytesIO(self._raw_ofs_bkgd))
            self.ofs_bkgd = Cameca.OffsetPos(self._root._io.pos(), _io__raw_ofs_bkgd, self, self._root)
            self.bkgd_under_peak_cps = self._io.read_f4le()
            self.bkgd_1_cps = self._io.read_f4le()
            self.bkgd_2_cps = self._io.read_f4le()
            self.ix_div_istd = self._io.read_f4le()
            self.ix_div_ipure = self._io.read_f4le()
            self.weight_fraction = self._io.read_f4le()
            self.norm_weight_frac = self._io.read_f4le()
            self.atomic_fraction = self._io.read_f4le()
            self.oxide_fraction = self._io.read_f4le()
            self.detection_limit = self._io.read_f4le()
            self.std_dev = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.a = self._io.read_f4le()
            self.f = self._io.read_f4le()
            self.not_re_1 = self._io.read_u4le()
            self.not_re_2 = self._io.read_f4le()
            self.not_re_3 = self._io.read_f4le()
            self.peak_raw_pulses = self._io.read_u4le()
            self.bkgd_1_raw_pulses = self._io.read_u4le()
            self.bkgd_2_raw_pulses = self._io.read_u4le()
            self.subcounting_mode = KaitaiStream.resolve_enum(Cameca.SubcountingMode, self._io.read_u4le())
            self.num_subcount = self._io.read_u4le()
            self.subcount_peak_enabled_flags = self._io.read_u4le()
            self.subcount_peak_pulses = []
            for i in range(self.num_subcount):
                self.subcount_peak_pulses.append(self._io.read_u4le())

            self.padding_0 = self._io.read_bytes(((30 - self.num_subcount) * 4))
            self.reserved_0 = self._io.read_bytes(4)
            self.subcount_bkgd1_enabled_flags = self._io.read_u4le()
            self.subcount_bkgd1_pulses = []
            for i in range(self.num_subcount):
                self.subcount_bkgd1_pulses.append(self._io.read_u4le())

            self.padding_1 = self._io.read_bytes(((30 - self.num_subcount) * 4))
            self.subcount_bkgd2_enabled_flags = self._io.read_u4le()
            self.subcount_bkgd2_pulses = []
            for i in range(self.num_subcount):
                self.subcount_bkgd2_pulses.append(self._io.read_u4le())

            self.padding_2 = self._io.read_bytes(((30 - self.num_subcount) * 4))
            self.bkgd_time = self._io.read_f4le()
            if self.version >= 11:
                self.padding_v11 = self._io.read_bytes(8)


        @property
        def bkgd_acq_time(self):
            """acq time ensuring correct background time; In normal (default) conditions
            in case peak counting hits 1M counts the background time is then set
            to half of that of peak (which terminates counting with 1M counter hit);
            In case using subcounting, such limititation does not apply.
            """
            if hasattr(self, '_m_bkgd_acq_time'):
                return self._m_bkgd_acq_time

            self._m_bkgd_acq_time = ((self.peak_time / 2) if  ((self.peak_raw_pulses >= 1000000) and (self.num_subcount == 1))  else self.bkgd_time)
            return getattr(self, '_m_bkgd_acq_time', None)


    class PolygonSelection(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = self._io.read_u4le()
            self.num_polygon_nodes = self._io.read_u4le()
            self.polygon_nodes = []
            for i in range(self.num_polygon_nodes):
                self.polygon_nodes.append(Cameca.PolygonPoint(self._io, self, self._root))



    class SxfHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.file_type = KaitaiStream.resolve_enum(Cameca.FileType, self._io.read_u1())
            self.magic = self._io.read_bytes(3)
            if not self.magic == b"\x66\x78\x73":
                raise kaitaistruct.ValidationNotEqualError(b"\x66\x78\x73", self.magic, self._io, u"/types/sxf_header/seq/1")
            self.sxf_version = self._io.read_u4le()
            self.comment = Cameca.CSharpString(self._io, self, self._root)
            self.reserved_0 = self._io.read_bytes(24)
            if self.sxf_version >= 3:
                self.reserved_v3 = self._io.read_bytes(4)

            if self.sxf_version >= 3:
                self.num_file_modifications = self._io.read_u4le()

            if self.sxf_version >= 3:
                self.file_modifications = []
                for i in range(self.num_file_modifications):
                    self.file_modifications.append(Cameca.FileModification(self._io, self, self._root))


            if self.sxf_version >= 4:
                self.reserved_v4 = self._io.read_bytes(8)

            if self.sxf_version >= 5:
                self.reserved_v5 = self._io.read_f8le()



    class QuantiWdsScan(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.n_channels = self._io.read_u4le()
            if self.n_channels > 0:
                self.start_pos = self._io.read_f4le()

            if self.n_channels > 0:
                self.step = self._io.read_f4le()

            if self.n_channels > 0:
                self.dwell_time = self._io.read_f4le()

            if self.n_channels > 0:
                self.data = self._io.read_bytes((self.n_channels * 4))



    class LimitedSignalHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element = Cameca.ElementT(self._io, self, self._root)


    class SxfMain(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.focus_frequency = self._io.read_u4le()
            self.verify_xtal_after_flip = self._io.read_s4le()
            self.verify_xtal_before_start = self._io.read_s4le()
            self.bkgd_measure_every_nth = self._io.read_u4le()
            self.decontamination_time = self._io.read_u4le()
            self.num_datasets = self._io.read_u4le()
            self.datasets = []
            for i in range(self.num_datasets):
                self.datasets.append(Cameca.Dataset(self._io, self, self._root))

            self.not_re_global_options = self._io.read_bytes(12)
            self.current_qti_set = Cameca.CSharpString(self._io, self, self._root)
            self.not_re_global_options_2 = self._io.read_bytes(216)
            if self.version >= 12:
                self.not_re_global_options_v12 = self._io.read_bytes(4)

            if self.version >= 13:
                self.eds_acquisition_time = self._io.read_f4le()

            if self.version >= 13:
                self.not_re_global_option_v13 = self._io.read_bytes(4)



    class StochAndDifferenceInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(4)
            self.element_for_stochiometry = Cameca.ElementT(self._io, self, self._root)
            self.num_oxy_state_changes = self._io.read_u4le()
            self.oxy_state_changes = []
            for i in range(self.num_oxy_state_changes):
                self.oxy_state_changes.append(Cameca.ElementOxyState(self._io, self, self._root))

            self.element_by_difference = Cameca.ElementT(self._io, self, self._root)


    class QtiEdsMeasurementSetup(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_u4le()
            self.element = Cameca.ElementT(self._io, self, self._root)
            self.xray_line = KaitaiStream.resolve_enum(Cameca.XrayLine, self._io.read_u4le())
            self.reserved_1 = self._io.read_u4le()
            self.calibration_setup_file = Cameca.CSharpString(self._io, self, self._root)
            self.reserved_2 = self._io.read_u4le()


    class VideoSignalHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.channel = self._io.read_u4le()
            self.video_signal_type = KaitaiStream.resolve_enum(Cameca.VideoSignalType, self._io.read_u4le())
            self.padding_0 = self._io.read_bytes(24)
            self.hv = self._io.read_f4le()
            self.beam_current = self._io.read_f4le()
            self.padding_1 = self._io.read_bytes(28)


    class StandardCompositionTable(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.standard_name = Cameca.CSharpString(self._io, self, self._root)
            self.num_element_weights = self._io.read_u4le()
            self.element_weights = []
            for i in range(self.num_element_weights):
                self.element_weights.append(Cameca.ElementWeight(self._io, self, self._root))



    class QtiWdsMeasurementSetup(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element = Cameca.ElementT(self._io, self, self._root)
            self.xray_line = KaitaiStream.resolve_enum(Cameca.XrayLine, self._io.read_u4le())
            self.spect_number = self._io.read_u4le()
            self._raw_xtal = self._io.read_bytes(4)
            _io__raw_xtal = KaitaiStream(BytesIO(self._raw_xtal))
            self.xtal = Cameca.XtalT(_io__raw_xtal, self, self._root)
            self.two_d = self._io.read_f4le()
            self.k = self._io.read_f4le()
            self.calibration_file = Cameca.CSharpString(self._io, self, self._root)
            self._raw_ofs_peak_bkgd = self._io.read_bytes(0)
            _io__raw_ofs_peak_bkgd = KaitaiStream(BytesIO(self._raw_ofs_peak_bkgd))
            self.ofs_peak_bkgd = Cameca.OffsetPos(self._root._io.pos(), _io__raw_ofs_peak_bkgd, self, self._root)
            self.reserved_0 = self._io.read_bytes(12)
            self.peak_position = self._io.read_u4le()
            self.peak_time = self._io.read_f4le()
            self.offset_bkgd_1 = self._io.read_s4le()
            self.offset_bkgd_2 = self._io.read_s4le()
            self.slope = self._io.read_f4le()
            self.bkgd_time = self._io.read_f4le()
            self.counter_setting = Cameca.CounterSetting(self._io, self, self._root)
            self.one_div_sqrt_n = self._io.read_f4le()
            self.reserved_1 = self._io.read_bytes(12)
            self.background_type = KaitaiStream.resolve_enum(Cameca.BackgroundType, self._io.read_u4le())
            self.reserved_2 = self._io.read_bytes(180)
            self.subcounting_flag = KaitaiStream.resolve_enum(Cameca.SubcountingMode, self._io.read_u4le())
            self.reserved_3 = self._io.read_bytes(156)
            if self._root.header.sxf_version >= 4:
                self.reserved_v4 = self._io.read_bytes(4)



    class BarLabel(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sec_name = Cameca.CSharpString(self._io, self, self._root)
            self.reserved_0 = self._io.read_bytes(40)


    class ByDifferenceInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element_by_difference = Cameca.ElementT(self._io, self, self._root)


    class FileModification(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = Cameca.DatetimeT(self._io, self, self._root)
            self.len_attributes = self._io.read_u4le()
            self._raw_attributes = self._io.read_bytes(self.len_attributes)
            _io__raw_attributes = KaitaiStream(BytesIO(self._raw_attributes))
            self.attributes = Cameca.ModificationAttributes(_io__raw_attributes, self, self._root)


    class SpaceTime(KaitaiStruct):
        """this struct allways contains valid datetime;
        If dataset is composed from multiple items this struct
        also will contain valid x,y and z stage coordinates;
        otherwise often those attributes here are zeros.
        Also this section holds calculated age and 1sigma error, if
        age calculation was done and saved with peaksight.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.datetime = Cameca.DatetimeT(self._io, self, self._root)
            self.x_axis = self._io.read_f4le()
            self.y_axis = self._io.read_f4le()
            self.z_axis = self._io.read_f4le()
            self.reserved_0 = self._io.read_bytes(8)
            self.not_re_0 = self._io.read_u4le()
            self.age = self._io.read_f4le()
            self.age_err = self._io.read_f4le()
            self.reserved_1 = self._io.read_bytes(56)
            if self.version == 6:
                self.reserved_v6 = self._io.read_bytes(24)



    class MacRecord(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.absorbing_element = self._io.read_u1()
            self.measured_element = self._io.read_u1()
            self.line = KaitaiStream.resolve_enum(Cameca.XrayLine, self._io.read_u2le())
            self.value = self._io.read_f4le()


    class DtsQtiFooter(KaitaiStruct):
        def __init__(self, dts_extras_type, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.dts_extras_type = dts_extras_type
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(4)
            self.num_datetime_and_pos = self._io.read_u4le()
            self.datetime_and_pos = []
            for i in range(self.num_datetime_and_pos):
                self.datetime_and_pos.append(Cameca.SpaceTime(self._io, self, self._root))

            self.quantification_options = Cameca.QuantiOptions(self._io, self, self._root)
            self.reserved_3 = self._io.read_bytes(12)
            if self.dts_extras_type == Cameca.DatasetExtrasType.qti_v6_footer:
                self.reserved_4 = self._io.read_bytes(4)

            if self.dts_extras_type == Cameca.DatasetExtrasType.qti_v6_footer:
                self.mac_table = Cameca.EmbeddedMacTable(self._io, self, self._root)



    class ColorTick(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.color = self._io.read_u4le()
            self.l_value = self._io.read_f4le()


    class CalSetup(KaitaiStruct):
        """this is a rought reverse engineared and far from complete."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(12)
            self.num_subsetups = self._io.read_u4le()
            self.subsetups = []
            for i in range(self.num_subsetups):
                self.subsetups.append(Cameca.SubSetup(self._io, self, self._root))

            self.calibration_options = Cameca.CalOptions(self._io, self, self._root)


    class ImgFooterSubsection(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.phase_something_str = Cameca.CSharpString(self._io, self, self._root)
            self.reserved_0 = self._io.read_bytes(292)
            self.overlayed_dataset = Cameca.CSharpString(self._io, self, self._root)
            self.reserved_01 = self._io.read_bytes(4)
            self.mosaic_rows = self._io.read_u4le()
            self.mosaic_cols = self._io.read_u4le()
            self.mosaic_tiling_states = []
            for i in range((self.mosaic_rows * self.mosaic_cols)):
                self.mosaic_tiling_states.append(self._io.read_s1())



    class CalibItem(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.beam_current = self._io.read_f4le()
            self.peak_cps = self._io.read_f4le()
            self.peak_time = self._io.read_f4le()
            self.bkgd_inter_cps = self._io.read_f4le()
            self.bkgd_1_cps = self._io.read_f4le()
            self.bkgd_2_cps = self._io.read_f4le()
            self.enabled = self._io.read_u4le()
            self.peak_raw_cts = self._io.read_s4le()
            self.bkgd_1_raw_cts = self._io.read_s4le()
            self.bkgd_2_raw_cts = self._io.read_s4le()
            self.reserved_1 = self._io.read_s4le()
            self.reserved_2 = self._io.read_s4le()
            self.reserved_3 = self._io.read_s4le()
            self.reserved_4 = self._io.read_bytes_full()

        @property
        def net_intensity(self):
            if hasattr(self, '_m_net_intensity'):
                return self._m_net_intensity

            self._m_net_intensity = ((self.peak_cps - self.bkgd_inter_cps) / self.beam_current)
            return getattr(self, '_m_net_intensity', None)


    class XtalT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.first_byte = self._io.read_u1()

        @property
        def rev_name(self):
            if hasattr(self, '_m_rev_name'):
                return self._m_rev_name

            _pos = self._io.pos()
            self._io.seek((0 if self.first_byte > 32 else 1))
            self._m_rev_name = (self._io.read_bytes_full()).decode(u"CP1252")
            self._io.seek(_pos)
            return getattr(self, '_m_rev_name', None)

        @property
        def full_name(self):
            if hasattr(self, '_m_full_name'):
                return self._m_full_name

            self._m_full_name = (self.rev_name)[::-1]
            return getattr(self, '_m_full_name', None)

        @property
        def family_name(self):
            if hasattr(self, '_m_family_name'):
                return self._m_family_name

            self._m_family_name = ((self.rev_name)[0:3])[::-1]
            return getattr(self, '_m_family_name', None)


    class OverlapCorrectionsContent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(4)
            self.num_overlap_corrections = self._io.read_u4le()
            self.overlap_corrections = []
            for i in range(self.num_overlap_corrections):
                self.overlap_corrections.append(Cameca.OverlapTableItem(self._io, self, self._root))



    class DatetimeT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ms_filetime = self._io.read_u8le()

        @property
        def unix_timestamp(self):
            """seconds since Jan 1 1970."""
            if hasattr(self, '_m_unix_timestamp'):
                return self._m_unix_timestamp

            self._m_unix_timestamp = ((self.ms_filetime / 10000000) - 11644473600)
            return getattr(self, '_m_unix_timestamp', None)


    class DatasetHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.dataset_type = KaitaiStream.resolve_enum(Cameca.DatasetType, self._io.read_u4le())
            self.stage_x = self._io.read_s4le()
            self.stage_y = self._io.read_s4le()
            self.beam_x = self._io.read_f4le()
            self.beam_y = self._io.read_f4le()
            self.step_x = self._io.read_f4le()
            self.step_y = self._io.read_f4le()
            self.n_of_steps = self._io.read_u4le()
            self.n_of_lines = self._io.read_u4le()
            self.not_re_dataset_flags = []
            for i in range(3):
                self.not_re_dataset_flags.append(self._io.read_s4le())

            self.n_accumulation = self._io.read_u4le()
            self.dwell_time = self._io.read_f4le()
            self.not_re_dataset_flag_4 = self._io.read_s4le()
            self.stage_z = []
            for i in range(49):
                self.stage_z.append(self._io.read_s4le())

            self.not_re_flags2 = []
            for i in range(2):
                self.not_re_flags2.append(self._io.read_s4le())

            self.beam_measurement_freq = self._io.read_f4le()
            self.not_re_flags3 = []
            for i in range(2):
                self.not_re_flags3.append(self._io.read_s4le())

            self.mosaic_cols = self._io.read_u4le()
            self.mosaic_rows = self._io.read_u4le()
            self.focus_freq = self._io.read_u4le()
            self.load_setup_every_nth = self._io.read_s4le()
            self.not_re_flag4 = self._io.read_s4le()
            self.setup_file_name = Cameca.CSharpString(self._io, self, self._root)
            self.n_of_elements = self._io.read_u4le()

        @property
        def n_of_points(self):
            if hasattr(self, '_m_n_of_points'):
                return self._m_n_of_points

            self._m_n_of_points = (self.n_of_steps * self.n_of_lines)
            return getattr(self, '_m_n_of_points', None)

        @property
        def n_of_tiles(self):
            if hasattr(self, '_m_n_of_tiles'):
                return self._m_n_of_tiles

            self._m_n_of_tiles = (self.mosaic_cols * self.mosaic_rows)
            return getattr(self, '_m_n_of_tiles', None)

        @property
        def is_mosaic(self):
            if hasattr(self, '_m_is_mosaic'):
                return self._m_is_mosaic

            self._m_is_mosaic = self.n_of_tiles > 1
            return getattr(self, '_m_is_mosaic', None)


    class QtiWdsMeasurementSetups(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.qti_setup_reserved_0 = self._io.read_bytes(20)
            self.num_qti_wds_measurement_setups = self._io.read_u4le()
            self.qti_wds_measurement_setups = []
            for i in range(self.num_qti_wds_measurement_setups):
                self.qti_wds_measurement_setups.append(Cameca.QtiWdsMeasurementSetup(self._io, self, self._root))



    class ElementWeight(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element = Cameca.ElementT(self._io, self, self._root)
            self.weight_fraction = self._io.read_f4le()


    class WdsSetup(KaitaiStruct):
        """this is roughly reverse engineared and far from complete."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(12)
            self.wds_scan_spect_setups = []
            for i in range(5):
                self.wds_scan_spect_setups.append(Cameca.WdsScanSpectSetup(self._io, self, self._root))

            self.column_and_sem_setup = Cameca.SubSetup(self._io, self, self._root)


    class Dataset(KaitaiStruct):
        """Dataset is constructed form header, main and footer parts;
        in case of points in grid or line, main and footer parts are arrayed
        separately.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = Cameca.DatasetHeader(self._io, self, self._root)
            self.items = []
            for i in range(self.header.n_of_elements):
                self.items.append(Cameca.DatasetItem(self.header.n_of_points, self._io, self, self._root))

            self.comment = Cameca.CSharpString(self._io, self, self._root)
            self.reserved_0 = self._io.read_bytes(32)
            self.num_extra_wds_stuff = self._io.read_u4le()
            self.extra_wds_stuff = []
            for i in range(self.num_extra_wds_stuff):
                self.extra_wds_stuff.append(Cameca.WdsItemExtraEnding(self._io, self, self._root))

            self.has_overview_image = self._io.read_u4le()
            if self.has_overview_image == 1:
                self.polygon_selection = Cameca.PolygonSelection(self._io, self, self._root)

            if self.has_overview_image == 1:
                self.overview_image_dataset = Cameca.Dataset(self._io, self, self._root)

            if self.has_overview_image == 1:
                self.polygon_selection_type = KaitaiStream.resolve_enum(Cameca.PolygonSelectionMode, self._io.read_u4le())

            self.is_video_capture_mode = self._io.read_u4le()
            self.reserved_1 = self._io.read_bytes(96)
            if self.header.version >= 17:
                self.reserved_v17 = self._io.read_bytes(4)

            if self.header.version >= 17:
                self.image_frames = self._io.read_u4le()

            if self.header.version >= 17:
                self.reserved_2 = self._io.read_bytes(4)

            if self.header.version >= 17:
                self.overscan_x = self._io.read_f4le()

            if self.header.version >= 17:
                self.overscan_y = self._io.read_f4le()

            if self.header.version >= 18:
                self.reserved_v18 = self._io.read_bytes(4)

            if self.header.version >= 19:
                self.reserved_v19 = self._io.read_bytes(12)

            self.dts_extras_type = KaitaiStream.resolve_enum(Cameca.DatasetExtrasType, self._io.read_u4le())
            _on = self.dts_extras_type
            if _on == Cameca.DatasetExtrasType.img_sec_footer:
                self.extras = Cameca.DtsImgSecFooter(self._io, self, self._root)
            elif _on == Cameca.DatasetExtrasType.wds_and_cal_footer:
                self.extras = Cameca.DtsWdsCalibFooter(self._io, self, self._root)
            elif _on == Cameca.DatasetExtrasType.qti_v5_footer:
                self.extras = Cameca.DtsQtiFooter(self.dts_extras_type, self._io, self, self._root)
            elif _on == Cameca.DatasetExtrasType.qti_v6_footer:
                self.extras = Cameca.DtsQtiFooter(self.dts_extras_type, self._io, self, self._root)


    class ImgWdsSpectSetup(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_xtal = self._io.read_bytes(4)
            _io__raw_xtal = KaitaiStream(BytesIO(self._raw_xtal))
            self.xtal = Cameca.XtalT(_io__raw_xtal, self, self._root)
            self.two_d = self._io.read_f4le()
            self.k = self._io.read_f4le()
            self.peak_position = self._io.read_u4le()
            self.element = Cameca.ElementT(self._io, self, self._root)
            self.xray_line = KaitaiStream.resolve_enum(Cameca.XrayLine, self._io.read_u4le())
            self.order = self._io.read_u4le()
            self.counter_setting = Cameca.CounterSetting(self._io, self, self._root)
            self.padding_0 = self._io.read_bytes(12)


    class AnnotatedLine(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element = Cameca.ElementT(self._io, self, self._root)
            self.line = KaitaiStream.resolve_enum(Cameca.XrayLine, self._io.read_u4le())
            self.order = self._io.read_u4le()
            self.reserverd1 = self._io.read_u4le()
            self.reserverd2 = self._io.read_u4le()


    class CSharpString(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.str_len = self._io.read_u4le()
            self.text = (self._io.read_bytes(self.str_len)).decode(u"CP1252")


    class EmbeddedMacTable(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mac_name = Cameca.CSharpString(self._io, self, self._root)
            self.num_macs = self._io.read_u4le()
            self.macs = []
            for i in range(self.num_macs):
                self.macs.append(Cameca.MacRecord(self._io, self, self._root))



    class StochiometryInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(4)
            self.element_for_stochiometry = Cameca.ElementT(self._io, self, self._root)
            self.num_oxy_state_changes = self._io.read_u4le()
            self.oxy_state_changes = []
            for i in range(self.num_oxy_state_changes):
                self.oxy_state_changes.append(Cameca.ElementOxyState(self._io, self, self._root))



    class ImgSetup(KaitaiStruct):
        """this is roughly RE and far from complete."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(12)
            self.num_subsetups = self._io.read_u4le()
            self.subsetups = []
            for i in range(self.num_subsetups):
                self.subsetups.append(Cameca.SubSetup(self._io, self, self._root))



    class ElementOxyState(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element = Cameca.ElementT(self._io, self, self._root)
            self.oxy_state = self._io.read_f4le()


    class QuantiOptions(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.qti_analysis_mode = KaitaiStream.resolve_enum(Cameca.AnalysisMode, self._io.read_u4le())
            _on = self.qti_analysis_mode
            if _on == Cameca.AnalysisMode.by_stochiometry:
                self.analysis_mode_info = Cameca.StochiometryInfo(self._io, self, self._root)
            elif _on == Cameca.AnalysisMode.matrix_def_and_stoch:
                self.analysis_mode_info = Cameca.MatrixDefinitionAndStochInfo(self._io, self, self._root)
            elif _on == Cameca.AnalysisMode.with_matrix_definition:
                self.analysis_mode_info = Cameca.MatrixDefinitionInfo(self._io, self, self._root)
            elif _on == Cameca.AnalysisMode.by_difference:
                self.analysis_mode_info = Cameca.ByDifferenceInfo(self._io, self, self._root)
            elif _on == Cameca.AnalysisMode.stoch_and_difference:
                self.analysis_mode_info = Cameca.StochAndDifferenceInfo(self._io, self, self._root)
            self.reserved_2 = self._io.read_bytes(12)
            self.matrix_correction_model = KaitaiStream.resolve_enum(Cameca.MatrixCorrectionType, self._io.read_u4le())
            self.geo_species_name = Cameca.CSharpString(self._io, self, self._root)


    class QtiSetup(KaitaiStruct):
        """this is a rought reverse engineared and far from complete."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.count_sync = self._io.read_u4le()
            self.reserved_0 = self._io.read_bytes(4)
            self.num_subsetups = self._io.read_u4le()
            self.subsetups = []
            for i in range(self.num_subsetups):
                self.subsetups.append(Cameca.SubSetup(self._io, self, self._root))

            self.reserved_1 = self._io.read_u4le()
            self.fixed_order = self._io.read_u4le()
            self.reserved_2 = self._io.read_bytes(16)
            self.quantification_options = Cameca.QuantiOptions(self._io, self, self._root)
            self.same_line_multi_spect_handling = KaitaiStream.resolve_enum(Cameca.MSpectSameLineHandling, self._io.read_u4le())
            if self._root.header.sxf_version >= 4:
                self.reserved_v20 = self._io.read_bytes(140)



    class WdsScanSignal(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.wds_start_pos = self._io.read_u4le()
            self.steps = self._io.read_u4le()
            self.step_size = self._io.read_f4le()
            self.dwell_time = self._io.read_f4le()
            self.beam_size = self._io.read_u4le()
            self.data_array_size = self._io.read_u4le()
            self.data = Cameca.LazyData(self._root._io.pos(), self.data_array_size, self._io, self, self._root)
            self.not_re_flag = self._io.read_u4le()
            self.signal_name = Cameca.CSharpString(self._io, self, self._root)
            self.reserved_0 = self._io.read_bytes(4)
            self.smoothing_pts = self._io.read_u4le()
            self.min_x = self._io.read_f4le()
            self.max_x = self._io.read_f4le()
            self.min_y = self._io.read_f4le()
            self.max_y = self._io.read_f4le()
            self.curve_color = self._io.read_bytes(4)
            self.reserved_1 = self._io.read_bytes(8)
            self.curve_type = self._io.read_u4le()
            self.curve_width = self._io.read_u4le()
            self.reserved_2 = self._io.read_bytes(4)
            self.lut_name = Cameca.CSharpString(self._io, self, self._root)
            self.reserved_3 = self._io.read_bytes(52)
            self.num_annotated_lines = self._io.read_u4le()
            self.annotated_lines = []
            for i in range(self.num_annotated_lines):
                self.annotated_lines.append(Cameca.AnnotatedLine(self._io, self, self._root))

            self.reserved_4 = self._io.read_bytes(4)
            self.num_extra_ending = self._io.read_u4le()
            self.extra_ending = []
            for i in range(self.num_extra_ending):
                self.extra_ending.append(Cameca.WdsItemExtraEnding(self._io, self, self._root))



    class MatrixDefinitionAndStochInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(4)
            self.element_for_stochiometry = Cameca.ElementT(self._io, self, self._root)
            self.num_oxy_state_changes = self._io.read_u4le()
            self.oxy_state_changes = []
            for i in range(self.num_oxy_state_changes):
                self.oxy_state_changes.append(Cameca.ElementOxyState(self._io, self, self._root))

            self.reserved_2 = self._io.read_bytes(4)
            self.num_element_weights = self._io.read_u4le()
            self.element_weights = []
            for i in range(self.num_element_weights):
                self.element_weights.append(Cameca.ElementWeight(self._io, self, self._root))



    class WdsQtiSignal(KaitaiStruct):
        def __init__(self, n_points, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.n_points = n_points
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.dataset_type = KaitaiStream.resolve_enum(Cameca.DatasetType, self._io.read_u4le())
            self.data_size = self._io.read_u4le()
            self.data = []
            for i in range(self.n_points):
                self.data.append(Cameca.QtiDataItem(self._io, self, self._root))

            self.reserved_0 = self._io.read_u4le()
            self.standard_name = Cameca.CSharpString(self._io, self, self._root)
            self.num_standard_weights = self._io.read_u4le()
            self.standard_weights = []
            for i in range(self.num_standard_weights):
                self.standard_weights.append(Cameca.ElementWeight(self._io, self, self._root))

            self.calib_hv = self._io.read_f4le()
            self.calib_current = self._io.read_f4le()
            self.i_standard = self._io.read_f4le()
            self.i_standard_std = self._io.read_f4le()
            self.calibration_file_name = Cameca.CSharpString(self._io, self, self._root)
            self.calib_peak_time = self._io.read_f4le()
            self.calib_bkgd_time = self._io.read_f4le()
            self._raw_ofs_bkgd_setup = self._io.read_bytes(0)
            _io__raw_ofs_bkgd_setup = KaitaiStream(BytesIO(self._raw_ofs_bkgd_setup))
            self.ofs_bkgd_setup = Cameca.OffsetPos(self._root._io.pos(), _io__raw_ofs_bkgd_setup, self, self._root)
            self.bkgd_1_pos = self._io.read_s4le()
            self.bkgd_2_pos = self._io.read_s4le()
            self.bkgd_slope = self._io.read_f4le()
            self.quanti_mode = KaitaiStream.resolve_enum(Cameca.QuantiMode, self._io.read_u4le())
            self.pk_area_range = self._io.read_u4le()
            self.pk_area_channels = self._io.read_u4le()
            self.pk_area_bkgd_1 = self._io.read_s4le()
            self.pk_area_bkgd2 = self._io.read_s4le()
            self.pk_area_n_accumulation = self._io.read_u4le()
            self.not_re_pk_area_flags = self._io.read_bytes(36)
            self.num_pk_area_wds_spectra = self._io.read_u4le()
            self.pk_area_wds_spectra = []
            for i in range(self.num_pk_area_wds_spectra):
                self.pk_area_wds_spectra.append(Cameca.QuantiWdsScan(self._io, self, self._root))

            if self._root.header.sxf_version > 3:
                self.not_re_calib_block = self._io.read_bytes(8)



    class EmptySignalHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dummy = self._io.read_bytes(68)


    class OverlapTableItem(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.element = Cameca.ElementT(self._io, self, self._root)
            self.line = KaitaiStream.resolve_enum(Cameca.XrayLine, self._io.read_u4le())
            self.i_element = self._io.read_u4le()
            self.i_line = KaitaiStream.resolve_enum(Cameca.XrayLine, self._io.read_u4le())
            self.i_order = self._io.read_u4le()
            self.i_offset = self._io.read_s4le()
            self.hv = self._io.read_f4le()
            self.beam_current = self._io.read_f4le()
            self.peak_min_bkgd = self._io.read_f4le()
            self.standard_name = Cameca.CSharpString(self._io, self, self._root)
            self.nr_in_standard_db = self._io.read_u4le()
            self.spect_nr = self._io.read_u4le()
            self._raw_xtal = self._io.read_bytes(4)
            _io__raw_xtal = KaitaiStream(BytesIO(self._raw_xtal))
            self.xtal = Cameca.XtalT(_io__raw_xtal, self, self._root)
            if self.version >= 3:
                self.dwell_time = self._io.read_f4le()

            if self.version >= 3:
                self.reserved_0 = self._io.read_bytes(4)



    class CalOptions(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved = self._io.read_bytes(24)
            self.standard_id = self._io.read_u4le()
            self.standard_name = Cameca.CSharpString(self._io, self, self._root)


    class MatrixDefinitionInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(4)
            self.num_element_weights = self._io.read_u4le()
            self.element_weights = []
            for i in range(self.num_element_weights):
                self.element_weights.append(Cameca.ElementWeight(self._io, self, self._root))




