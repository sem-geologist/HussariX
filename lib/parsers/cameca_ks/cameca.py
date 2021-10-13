# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

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
        self.header = self._root.SxfHeader(self._io, self, self._root)
        _on = self.header.file_type
        if _on == self._root.FileType.calibration_results:
            self.content = self._root.SxfMain(self._io, self, self._root)
        elif _on == self._root.FileType.image_mapping_setup:
            self.content = self._root.ImgSetup(self._io, self, self._root)
        elif _on == self._root.FileType.image_mapping_results:
            self.content = self._root.SxfMain(self._io, self, self._root)
        elif _on == self._root.FileType.wds_results:
            self.content = self._root.SxfMain(self._io, self, self._root)
        elif _on == self._root.FileType.wds_setup:
            self.content = self._root.WdsSetup(self._io, self, self._root)
        elif _on == self._root.FileType.quanti_results:
            self.content = self._root.SxfMain(self._io, self, self._root)
        elif _on == self._root.FileType.quanti_setup:
            self.content = self._root.QtiSetup(self._io, self, self._root)
        elif _on == self._root.FileType.overlap_table:
            self.content = self._root.OverlapCorrections(self._io, self, self._root)
        elif _on == self._root.FileType.calibration_setup:
            self.content = self._root.CalSetup(self._io, self, self._root)

    class AnnotatedLines(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element = self._root.ElementT(self._io, self, self._root)
            self.line = self._root.XrayLine(self._io.read_u4le())
            self.order = self._io.read_u4le()
            self.reserverd1 = self._io.read_u4le()
            self.reserverd2 = self._io.read_u4le()


    class DtsWdsCalibFooter(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if self._root.header.file_type == self._root.FileType.calibration_results:
                self.reserved_0 = self._io.read_bytes(4)

            if self._root.header.file_type == self._root.FileType.calibration_results:
                self.n_space_time = self._io.read_u4le()

            self.datetime_and_pos = [None] * ((self.n_space_time if self._root.header.file_type == self._root.FileType.calibration_results else 1))
            for i in range((self.n_space_time if self._root.header.file_type == self._root.FileType.calibration_results else 1)):
                self.datetime_and_pos[i] = self._root.SpaceTime(self._io, self, self._root)

            self.reserved_1 = self._io.read_bytes(4)
            if self._root.header.file_type.value != 8:
                self.reserved_wds_ending_1 = self._io.read_bytes(4)

            if self._root.header.file_type.value != 8:
                self.dataset_is_selected = self._io.read_u4le()

            if self._root.header.file_type.value != 8:
                self.reserved_wds_ending_2 = self._io.read_bytes(40)

            if self._root.header.file_type.value == 8:
                self.standard = self._root.StandardCompositionTable(self._io, self, self._root)



    class XraySignalHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element = self._root.ElementT(self._io, self, self._root)
            self.xray_line = self._root.XrayLine(self._io.read_u4le())
            self.order = self._io.read_u4le()
            self.spect_no = self._io.read_u4le()
            self._raw_xtal = self._io.read_bytes(4)
            io = KaitaiStream(BytesIO(self._raw_xtal))
            self.xtal = self._root.XtalT(io, self, self._root)
            self.two_d = self._io.read_f4le()
            self.k = self._io.read_f4le()
            self.reserved_0 = self._io.read_bytes(4)
            self.hv_set = self._io.read_f4le()
            self.beam_current = self._io.read_f4le()
            self.peak_pos = self._io.read_u4le()
            self.counter_setting = self._root.CounterSetting(self._io, self, self._root)

        @property
        def combi_string(self):
            if hasattr(self, '_m_combi_string'):
                return self._m_combi_string if hasattr(self, '_m_combi_string') else None

            if self._parent.signal_type == self._root.SignalSource.wds:
                self._m_combi_string = str(self.spect_no) + u": " + self.xtal.full_name

            return self._m_combi_string if hasattr(self, '_m_combi_string') else None


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
            self.condition_name = self._root.CSharpString(self._io, self, self._root)
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
            self.reserved_flags_5 = [None] * (6)
            for i in range(6):
                self.reserved_flags_5[i] = self._io.read_s4le()

            self.extractor = self._io.read_s4le()
            self.suppressor = self._io.read_s4le()
            self.reserved_flags_6 = [None] * ((86 if self._root.header.file_type.value > 1 else 85))
            for i in range((86 if self._root.header.file_type.value > 1 else 85)):
                self.reserved_flags_6[i] = self._io.read_s4le()

            if self._root.header.file_type.value > 1:
                self.n_eds_measurement_setups = self._io.read_u4le()

            if self._root.header.file_type.value > 1:
                self.eds_measurement_setups = [None] * (self.n_eds_measurement_setups)
                for i in range(self.n_eds_measurement_setups):
                    self.eds_measurement_setups[i] = self._root.QtiEdsMeasurementSetup(self._io, self, self._root)


            self.default_eds_live_time = self._io.read_f4le()
            self.not_re_flag_5 = self._io.read_u4le()
            self.eds_roi_fwhm = self._io.read_f4le()
            self.reserved_flags_7 = self._io.read_bytes(8)
            if self._root.header.file_type.value > 1:
                self.wds_measurement_struct_type = self._io.read_u4le()

            if self.wds_measurement_struct_type == 3:
                self.wds_img_spect_setups = self._root.ImgWdsSpectSetups(self._io, self, self._root)

            if self.wds_measurement_struct_type >= 19:
                self.wds_qti_measurement_setups = self._root.QtiWdsMeasurementSetups(self._io, self, self._root)



    class CalibSignal(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.data_size = self._io.read_u4le()
            self.unkn_x = self._io.read_bytes(4)
            self.total_size = self._io.read_u4le()
            self._raw_data = [None] * (self.total_size // self.data_size)
            self.data = [None] * (self.total_size // self.data_size)
            for i in range(self.total_size // self.data_size):
                self._raw_data[i] = self._io.read_bytes(self.data_size)
                io = KaitaiStream(BytesIO(self._raw_data[i]))
                self.data[i] = self._root.CalibItem(io, self, self._root)

            self.calib_peak_time = self._io.read_f4le()
            self.calib_bkgd_time = self._io.read_f4le()
            self.bkgd_1_pos = self._io.read_s4le()
            self.bkgd_2_pos = self._io.read_s4le()
            self.bkgd_slope = self._io.read_f4le()
            self.quanti_mode = self._root.QuantiMode(self._io.read_u4le())
            self.pk_area_range = self._io.read_u4le()
            self.pk_area_channels = self._io.read_u4le()
            self.pk_area_bkgd_1 = self._io.read_s4le()
            self.pk_area_bkgd_2 = self._io.read_s4le()
            self.pk_area_n_accumulation = self._io.read_u4le()
            self.not_re_area_flags = self._io.read_bytes(24)
            self.n_calib_points = self._io.read_u4le()
            self.pk_area_wds_spetras = [None] * (self.n_calib_points)
            for i in range(self.n_calib_points):
                self.pk_area_wds_spetras[i] = self._root.QuantiWdsScan(self._io, self, self._root)



    class WdsItemExtraEnding(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.item_comment = self._root.CSharpString(self._io, self, self._root)
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
            io = KaitaiStream(BytesIO(self._raw_xtal))
            self.xtal = self._root.XtalT(io, self, self._root)
            self.two_d = self._io.read_f4le()
            self.k = self._io.read_f4le()
            self.wds_scan_type = self._root.WdsScanType(self._io.read_u4le())
            self.min_pos = self._io.read_u4le()
            self.reserved_1 = self._io.read_u4le()
            self.reserved_2 = self._io.read_u4le()
            self.reserved_3 = self._io.read_u4le()
            self.max_pos = self._io.read_u4le()
            self.reserved_4 = self._io.read_bytes((4 * 3))
            self.position = self._io.read_u4le()
            self.element = self._root.ElementT(self._io, self, self._root)
            self.xray_line = self._root.XrayLine(self._io.read_u4le())
            self.order = self._io.read_u4le()
            self.offset_1 = self._io.read_s4le()
            self.offset_2 = self._io.read_s4le()
            self.counter_setting = self._root.CounterSetting(self._io, self, self._root)


    class DatasetItem(KaitaiStruct):
        def __init__(self, n_points, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.n_points = n_points
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.signal_type = self._root.SignalSource(self._io.read_u4le())
            _on = self.signal_type
            if _on == self._root.SignalSource.qti_stoch:
                self._raw_signal_header = self._io.read_bytes(68)
                io = KaitaiStream(BytesIO(self._raw_signal_header))
                self.signal_header = self._root.LimitedSignalHeader(io, self, self._root)
            elif _on == self._root.SignalSource.qti_diff:
                self._raw_signal_header = self._io.read_bytes(68)
                io = KaitaiStream(BytesIO(self._raw_signal_header))
                self.signal_header = self._root.LimitedSignalHeader(io, self, self._root)
            elif _on == self._root.SignalSource.qti_matrix:
                self._raw_signal_header = self._io.read_bytes(68)
                io = KaitaiStream(BytesIO(self._raw_signal_header))
                self.signal_header = self._root.LimitedSignalHeader(io, self, self._root)
            elif _on == self._root.SignalSource.im_camera:
                self._raw_signal_header = self._io.read_bytes(68)
                io = KaitaiStream(BytesIO(self._raw_signal_header))
                self.signal_header = self._root.EmptySignalHeader(io, self, self._root)
            elif _on == self._root.SignalSource.video:
                self._raw_signal_header = self._io.read_bytes(68)
                io = KaitaiStream(BytesIO(self._raw_signal_header))
                self.signal_header = self._root.VideoSignalHeader(io, self, self._root)
            else:
                self._raw_signal_header = self._io.read_bytes(68)
                io = KaitaiStream(BytesIO(self._raw_signal_header))
                self.signal_header = self._root.XraySignalHeader(io, self, self._root)
            self.not_re_flag = self._io.read_u4le()
            self.reserved_0 = self._io.read_bytes(12)
            self.n_of_reserved_1_blocks = self._io.read_u4le()
            self.reserved_1_blocks = [None] * (self.n_of_reserved_1_blocks)
            for i in range(self.n_of_reserved_1_blocks):
                self.reserved_1_blocks[i] = self._io.read_bytes(12)

            _on = self._root.header.file_type
            if _on == self._root.FileType.image_mapping_results:
                self.signal = self._root.ImageProfileSignal(self.n_points, self._io, self, self._root)
            elif _on == self._root.FileType.wds_results:
                self.signal = self._root.WdsScanSignal(self._io, self, self._root)
            elif _on == self._root.FileType.quanti_results:
                self.signal = self._root.WdsQtiSignal(self.n_points, self._io, self, self._root)
            elif _on == self._root.FileType.calibration_results:
                self.signal = self._root.CalibSignal(self._io, self, self._root)


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
            self.mode = self._root.PhaMode(self._io.read_u4le())


    class DtsImgSecFooter(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.datetime_and_pos = self._root.SpaceTime(self._io, self, self._root)
            self.reserved_0 = self._io.read_bytes(4)
            self.reserved_1 = self._io.read_bytes(8)
            self.reserved_2 = self._io.read_bytes(64)
            self.n_subsections = self._io.read_u4le()
            self.subsections = [None] * (self.n_subsections)
            for i in range(self.n_subsections):
                self.subsections[i] = self._root.ImgFooterSubsection(self._io, self, self._root)



    class ImgWdsSpectSetups(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.wds_img_spect_setup_table = [None] * (5)
            for i in range(5):
                self.wds_img_spect_setup_table[i] = self._root.ImgWdsSpectSetup(self._io, self, self._root)



    class ColorBarTicks(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.n_color_bar_ticks = self._io.read_u4le()
            if self.n_color_bar_ticks > 0:
                self.colors = [None] * (self.n_color_bar_ticks)
                for i in range(self.n_color_bar_ticks):
                    self.colors[i] = self._root.ColorTick(self._io, self, self._root)


            if self.n_color_bar_ticks > 0:
                self.max_value = self._io.read_f4le()

            self.reserved_0 = self._io.read_f4le()
            self.reserved_1 = self._io.read_bytes(4)
            self.n_color_bar_labels = self._io.read_u4le()
            if self.n_color_bar_labels > 0:
                self.custom_color_bar_labels = [None] * (self.n_color_bar_labels)
                for i in range(self.n_color_bar_labels):
                    self.custom_color_bar_labels[i] = self._root.BarLabel(self._io, self, self._root)




    class ImageProfileSignal(KaitaiStruct):
        def __init__(self, n_pixels, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.n_pixels = n_pixels
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.dataset_type = self._root.DatasetType(self._io.read_u4le())
            self.stage_x = self._io.read_s4le()
            self.stage_y = self._io.read_s4le()
            self.beam_x = self._io.read_s4le()
            self.beam_y = self._io.read_s4le()
            self.step_x = self._io.read_f4le()
            self.step_y = self._io.read_f4le()
            self.width = self._io.read_u4le()
            self.height = self._io.read_u4le()
            self.z_axis = self._io.read_s4le()
            self.img_pixel_dtype = self._root.ImageArrayDtype(self._io.read_u4le())
            self.dwell_time = self._io.read_f4le()
            if  ((self.dataset_type != self._root.DatasetType.line_stage) and (self.dataset_type != self._root.DatasetType.line_beam)) :
                self.n_accumulation = self._io.read_u4le()

            self.not_re_flag = self._io.read_u4le()
            self.data_size = self._io.read_u4le()
            if  ((self.dataset_type != self._root.DatasetType.line_stage) and (self.dataset_type != self._root.DatasetType.line_beam)) :
                self.not_re_flag2 = self._io.read_u4le()

            if  ((self.dataset_type != self._root.DatasetType.line_stage) and (self.dataset_type != self._root.DatasetType.line_beam)) :
                self.not_re_flag3 = self._io.read_f4le()

            if  ((self.dataset_type != self._root.DatasetType.line_stage) and (self.dataset_type != self._root.DatasetType.line_beam)) :
                self.not_re_flag4 = self._io.read_f4le()

            self.data = [None] * (self.n_of_frames)
            for i in range(self.n_of_frames):
                self.data[i] = self._io.read_bytes(self.frame_size)

            self.reserved_0 = self._io.read_bytes(56)
            self.lut_name = self._root.CSharpString(self._io, self, self._root)
            self.signal_name = self._root.CSharpString(self._io, self, self._root)
            self.intensity_min = self._io.read_f4le()
            self.intensity_max = self._io.read_f4le()
            self.reserved_1 = self._io.read_bytes(20)
            self.visible_width = self._io.read_u4le()
            self.visible_height = self._io.read_u4le()
            self.colorbar_ticks = self._root.ColorBarTicks(self._io, self, self._root)
            self.img_rotation = self._io.read_f4le()
            self.reserved_2 = self._io.read_bytes(8)
            if self.version >= 6:
                self.reserved_v6 = self._io.read_bytes(12)


        @property
        def array_data_size(self):
            if hasattr(self, '_m_array_data_size'):
                return self._m_array_data_size if hasattr(self, '_m_array_data_size') else None

            self._m_array_data_size = (self.data_size - (0 if  ((self.dataset_type == self._root.DatasetType.line_stage) or (self.dataset_type == self._root.DatasetType.line_beam))  else 12))
            return self._m_array_data_size if hasattr(self, '_m_array_data_size') else None

        @property
        def frame_size(self):
            if hasattr(self, '_m_frame_size'):
                return self._m_frame_size if hasattr(self, '_m_frame_size') else None

            self._m_frame_size = ((1 if self.img_pixel_dtype.value == 0 else 4) * self.n_pixels)
            return self._m_frame_size if hasattr(self, '_m_frame_size') else None

        @property
        def n_of_frames(self):
            if hasattr(self, '_m_n_of_frames'):
                return self._m_n_of_frames if hasattr(self, '_m_n_of_frames') else None

            self._m_n_of_frames = self.array_data_size // self.frame_size
            return self._m_n_of_frames if hasattr(self, '_m_n_of_frames') else None


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
            self.subcounting_mode = self._root.SubcountingMode(self._io.read_u4le())
            self.n_sub_count = self._io.read_u4le()
            self.subcount_peak_enabled_flags = self._io.read_u4le()
            self.subcount_peak_pulses = [None] * (self.n_sub_count)
            for i in range(self.n_sub_count):
                self.subcount_peak_pulses[i] = self._io.read_u4le()

            self.padding_0 = self._io.read_bytes(((30 - self.n_sub_count) * 4))
            self.reserved_0 = self._io.read_bytes(4)
            self.subcount_bkgd1_enabled_flags = self._io.read_u4le()
            self.subcount_bkgd1_pulses = [None] * (self.n_sub_count)
            for i in range(self.n_sub_count):
                self.subcount_bkgd1_pulses[i] = self._io.read_u4le()

            self.padding_1 = self._io.read_bytes(((30 - self.n_sub_count) * 4))
            self.subcount_bkgd2_enabled_flags = self._io.read_u4le()
            self.subcount_bkgd2_pulses = [None] * (self.n_sub_count)
            for i in range(self.n_sub_count):
                self.subcount_bkgd2_pulses[i] = self._io.read_u4le()

            self.padding_2 = self._io.read_bytes(((30 - self.n_sub_count) * 4))
            self.bkgd_time = self._io.read_f4le()
            if self.version >= 11:
                self.padding_v11 = self._io.read_bytes(8)



    class SxfHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.file_type = self._root.FileType(self._io.read_u1())
            self.magic = self._io.ensure_fixed_contents(b"\x66\x78\x73")
            self.sxf_version = self._io.read_u4le()
            self.comment = self._root.CSharpString(self._io, self, self._root)
            self.reserved_0 = self._io.read_bytes(28)
            self.n_file_modifications = self._io.read_u4le()
            self.file_changes = [None] * (self.n_file_modifications)
            for i in range(self.n_file_modifications):
                self.file_changes[i] = self._root.FileModification(self._io, self, self._root)

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
            self.element = self._root.ElementT(self._io, self, self._root)


    class SxfMain(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.focus_frequency = self._io.read_u4le()
            self.verify_xtal_after_flip = self._io.read_u4le()
            self.verify_xtal_before_start = self._io.read_u4le()
            self.bkgd_measure_every_nth = self._io.read_u4le()
            self.decontamination_time = self._io.read_u4le()
            self.n_of_datasets = self._io.read_u4le()
            self.datasets = [None] * (self.n_of_datasets)
            for i in range(self.n_of_datasets):
                self.datasets[i] = self._root.Dataset(self._io, self, self._root)

            self.not_re_global_options = self._io.read_bytes(12)
            self.current_qti_set = self._root.CSharpString(self._io, self, self._root)
            self.not_re_global_options_2 = self._io.read_bytes(216)
            if self._root.header.sxf_version >= 4:
                self.not_re_global_options_v4 = self._io.read_bytes(12)



    class StochAndDifferenceInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(4)
            self.element_for_stochiometry = self._root.ElementT(self._io, self, self._root)
            self.n_changed_oxy_states = self._io.read_u4le()
            self.oxy_state_changes = [None] * (self.n_changed_oxy_states)
            for i in range(self.n_changed_oxy_states):
                self.oxy_state_changes[i] = self._root.ElementOxyState(self._io, self, self._root)

            self.element_by_difference = self._root.ElementT(self._io, self, self._root)


    class QtiEdsMeasurementSetup(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_u4le()
            self.element = self._root.ElementT(self._io, self, self._root)
            self.xray_line = self._root.XrayLine(self._io.read_u4le())
            self.reserved_1 = self._io.read_u4le()
            self.calibration_setup_file = self._root.CSharpString(self._io, self, self._root)
            self.reserved_2 = self._io.read_u4le()


    class VideoSignalHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.channel = self._io.read_u4le()
            self.video_signal_type = self._root.VideoSignalType(self._io.read_u4le())
            self.padding_0 = self._io.read_bytes(24)
            self.hv_set = self._io.read_f4le()
            self.beam_current = self._io.read_f4le()
            self.padding_1 = self._io.read_bytes(28)


    class StandardCompositionTable(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.standard_name = self._root.CSharpString(self._io, self, self._root)
            self.n_elements = self._io.read_u4le()
            self.standard_weight_table = [None] * (self.n_elements)
            for i in range(self.n_elements):
                self.standard_weight_table[i] = self._root.ElementWeight(self._io, self, self._root)



    class QtiWdsMeasurementSetup(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element = self._root.ElementT(self._io, self, self._root)
            self.xray_line = self._root.XrayLine(self._io.read_u4le())
            self.spect_number = self._io.read_u4le()
            self._raw_xtal = self._io.read_bytes(4)
            io = KaitaiStream(BytesIO(self._raw_xtal))
            self.xtal = self._root.XtalT(io, self, self._root)
            self.not_re_flag_0 = self._io.read_f4le()
            self.not_re_flag_1 = self._io.read_f4le()
            self.calibration_file = self._root.CSharpString(self._io, self, self._root)
            self.reserved_0 = self._io.read_bytes(12)
            self.peak_position = self._io.read_u4le()
            self.peak_time = self._io.read_f4le()
            self.offset_bkgd_1 = self._io.read_s4le()
            self.offset_bkgd_2 = self._io.read_s4le()
            self.slope = self._io.read_f4le()
            self.bkgd_time = self._io.read_f4le()
            self.counter_setting = self._root.CounterSetting(self._io, self, self._root)
            self.one_div_sqrt_n = self._io.read_f4le()
            self.reserved_1 = self._io.read_bytes(12)
            self.background_type = self._root.BackgroundType(self._io.read_u4le())
            self.reserved_2 = self._io.read_bytes(180)
            self.subcounting_flag = self._root.SubcountingMode(self._io.read_u4le())
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
            self.sec_name = self._root.CSharpString(self._io, self, self._root)
            self.reserved_0 = self._io.read_bytes(40)


    class ByDifferenceInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element_by_difference = self._root.ElementT(self._io, self, self._root)


    class FileModification(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = self._root.DatetimeT(self._io, self, self._root)
            self.len_of_bytestring = self._io.read_u4le()
            self._raw_attributes = self._io.read_bytes(self.len_of_bytestring)
            io = KaitaiStream(BytesIO(self._raw_attributes))
            self.attributes = self._root.ModificationAttributes(io, self, self._root)


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
            self.datetime = self._root.DatetimeT(self._io, self, self._root)
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



    class OverlapCorrections(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(4)
            self.n_corrections = self._io.read_u4le()
            self.overlap_correction_table = [None] * (self.n_corrections)
            for i in range(self.n_corrections):
                self.overlap_correction_table[i] = self._root.OverlapTableItem(self._io, self, self._root)



    class MacRecord(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.absorbing_element = self._io.read_u1()
            self.measured_element = self._io.read_u1()
            self.line = self._root.XrayLine(self._io.read_u2le())
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
            self.n_space_time = self._io.read_u4le()
            self.datetime_and_pos = [None] * (self.n_space_time)
            for i in range(self.n_space_time):
                self.datetime_and_pos[i] = self._root.SpaceTime(self._io, self, self._root)

            self.quantification_options = self._root.QuantiOptions(self._io, self, self._root)
            self.reserved_3 = self._io.read_bytes(12)
            if self.dts_extras_type == self._root.DatasetExtrasType.qti_v6_footer:
                self.reserved_4 = self._io.read_bytes(4)

            if self.dts_extras_type == self._root.DatasetExtrasType.qti_v6_footer:
                self.mac_table = self._root.EmbeddedMacTable(self._io, self, self._root)



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
            self.n_sub_setups = self._io.read_u4le()
            self.subsetups = [None] * (self.n_sub_setups)
            for i in range(self.n_sub_setups):
                self.subsetups[i] = self._root.SubSetup(self._io, self, self._root)

            self.calibration_options = self._root.CalOptions(self._io, self, self._root)


    class ImgFooterSubsection(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.phase_something_str = self._root.CSharpString(self._io, self, self._root)
            self.reserved_0 = self._io.read_bytes(300)
            self.mosaic_rows = self._io.read_u4le()
            self.mosaic_cols = self._io.read_u4le()
            self.mosaic_segment_enabled_flag_array = [None] * ((self.mosaic_rows * self.mosaic_cols))
            for i in range((self.mosaic_rows * self.mosaic_cols)):
                self.mosaic_segment_enabled_flag_array[i] = self._io.read_s1()



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
                return self._m_rev_name if hasattr(self, '_m_rev_name') else None

            _pos = self._io.pos()
            self._io.seek((0 if self.first_byte > 0 else 1))
            self._m_rev_name = (self._io.read_bytes_full()).decode(u"CP1252")
            self._io.seek(_pos)
            return self._m_rev_name if hasattr(self, '_m_rev_name') else None

        @property
        def full_name(self):
            if hasattr(self, '_m_full_name'):
                return self._m_full_name if hasattr(self, '_m_full_name') else None

            self._m_full_name = self.rev_name[::-1]
            return self._m_full_name if hasattr(self, '_m_full_name') else None

        @property
        def family_name(self):
            if hasattr(self, '_m_family_name'):
                return self._m_family_name if hasattr(self, '_m_family_name') else None

            self._m_family_name = self.rev_name[0:3][::-1]
            return self._m_family_name if hasattr(self, '_m_family_name') else None


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
                return self._m_unix_timestamp if hasattr(self, '_m_unix_timestamp') else None

            self._m_unix_timestamp = ((self.ms_filetime / 10000000) - 11644473600)
            return self._m_unix_timestamp if hasattr(self, '_m_unix_timestamp') else None


    class DatasetHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.dataset_type = self._root.DatasetType(self._io.read_u4le())
            self.stage_x = self._io.read_s4le()
            self.stage_y = self._io.read_s4le()
            self.beam_x = self._io.read_s4le()
            self.beam_y = self._io.read_s4le()
            self.step_x = self._io.read_f4le()
            self.step_y = self._io.read_f4le()
            self.n_of_steps = self._io.read_u4le()
            self.n_of_lines = self._io.read_u4le()
            self.not_re_dataset_flags = [None] * (3)
            for i in range(3):
                self.not_re_dataset_flags[i] = self._io.read_s4le()

            self.n_accumulation = self._io.read_u4le()
            self.dwell_time = self._io.read_f4le()
            self.not_re_dataset_flag_4 = self._io.read_s4le()
            self.stage_z = [None] * (49)
            for i in range(49):
                self.stage_z[i] = self._io.read_s4le()

            self.not_re_flags2 = [None] * (2)
            for i in range(2):
                self.not_re_flags2[i] = self._io.read_s4le()

            self.beam_measurement_freq = self._io.read_f4le()
            self.not_re_flags3 = [None] * (2)
            for i in range(2):
                self.not_re_flags3[i] = self._io.read_s4le()

            self.mosaic_cols = self._io.read_u4le()
            self.mosaic_rows = self._io.read_u4le()
            self.focus_freq = self._io.read_u4le()
            self.load_setup_everyth_nth = self._io.read_s4le()
            self.not_re_flag4 = self._io.read_s4le()
            self.setup_file_name = self._root.CSharpString(self._io, self, self._root)
            self.n_of_elements = self._io.read_u4le()

        @property
        def n_of_points(self):
            if hasattr(self, '_m_n_of_points'):
                return self._m_n_of_points if hasattr(self, '_m_n_of_points') else None

            self._m_n_of_points = (self.n_of_steps * self.n_of_lines)
            return self._m_n_of_points if hasattr(self, '_m_n_of_points') else None

        @property
        def n_of_tiles(self):
            if hasattr(self, '_m_n_of_tiles'):
                return self._m_n_of_tiles if hasattr(self, '_m_n_of_tiles') else None

            self._m_n_of_tiles = (self.mosaic_cols * self.mosaic_rows)
            return self._m_n_of_tiles if hasattr(self, '_m_n_of_tiles') else None

        @property
        def is_mosaic(self):
            if hasattr(self, '_m_is_mosaic'):
                return self._m_is_mosaic if hasattr(self, '_m_is_mosaic') else None

            self._m_is_mosaic = self.n_of_tiles > 1
            return self._m_is_mosaic if hasattr(self, '_m_is_mosaic') else None


    class QtiWdsMeasurementSetups(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.qti_setup_reserved_0 = self._io.read_bytes(20)
            self.n_wds_measurements = self._io.read_u4le()
            self.qti_wds_measurement_setups = [None] * (self.n_wds_measurements)
            for i in range(self.n_wds_measurements):
                self.qti_wds_measurement_setups[i] = self._root.QtiWdsMeasurementSetup(self._io, self, self._root)



    class ElementWeight(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element = self._root.ElementT(self._io, self, self._root)
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
            self.wds_scan_spect_setups = [None] * (5)
            for i in range(5):
                self.wds_scan_spect_setups[i] = self._root.WdsScanSpectSetup(self._io, self, self._root)

            self.column_and_sem_setup = self._root.SubSetup(self._io, self, self._root)


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
            self.header = self._root.DatasetHeader(self._io, self, self._root)
            self.items = [None] * (self.header.n_of_elements)
            for i in range(self.header.n_of_elements):
                self.items[i] = self._root.DatasetItem(self.header.n_of_points, self._io, self, self._root)

            self.comment = self._root.CSharpString(self._io, self, self._root)
            self.reserved_0 = self._io.read_bytes(32)
            self.n_extra_wds_stuff = self._io.read_u4le()
            self.extra_wds_stuff = [None] * (self.n_extra_wds_stuff)
            for i in range(self.n_extra_wds_stuff):
                self.extra_wds_stuff[i] = self._root.WdsItemExtraEnding(self._io, self, self._root)

            self.template_flag = self._io.read_u4le()
            if self.template_flag == 1:
                self.reserved_tmp_sector_0 = self._io.read_bytes(8)

            if self.template_flag == 1:
                self.template = self._root.Dataset(self._io, self, self._root)

            if self.template_flag == 1:
                self.reserved_tmp_sector_1 = self._io.read_bytes(4)

            self.reserved_1 = self._io.read_bytes(104)
            self.image_frames = self._io.read_u4le()
            self.reserved_2 = self._io.read_bytes(12)
            if self.header.version >= 18:
                self.reserved_v18 = self._io.read_bytes(4)

            if self.header.version >= 19:
                self.reserved_v19 = self._io.read_bytes(12)

            self.dts_extras_type = self._root.DatasetExtrasType(self._io.read_u4le())
            _on = self.dts_extras_type
            if _on == self._root.DatasetExtrasType.img_sec_footer:
                self.extras = self._root.DtsImgSecFooter(self._io, self, self._root)
            elif _on == self._root.DatasetExtrasType.wds_and_cal_footer:
                self.extras = self._root.DtsWdsCalibFooter(self._io, self, self._root)
            elif _on == self._root.DatasetExtrasType.qti_v5_footer:
                self.extras = self._root.DtsQtiFooter(self.dts_extras_type, self._io, self, self._root)
            elif _on == self._root.DatasetExtrasType.qti_v6_footer:
                self.extras = self._root.DtsQtiFooter(self.dts_extras_type, self._io, self, self._root)


    class ImgWdsSpectSetup(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_xtal = self._io.read_bytes(4)
            io = KaitaiStream(BytesIO(self._raw_xtal))
            self.xtal = self._root.XtalT(io, self, self._root)
            self.two_d = self._io.read_f4le()
            self.k = self._io.read_f4le()
            self.peak_position = self._io.read_u4le()
            self.element = self._root.ElementT(self._io, self, self._root)
            self.xray_line = self._root.XrayLine(self._io.read_u4le())
            self.order = self._io.read_u4le()
            self.counter_setting = self._root.CounterSetting(self._io, self, self._root)
            self.padding_0 = self._io.read_bytes(12)


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
            self.mac_name = self._root.CSharpString(self._io, self, self._root)
            self.n_records = self._io.read_u4le()
            self.mac_table = [None] * (self.n_records)
            for i in range(self.n_records):
                self.mac_table[i] = self._root.MacRecord(self._io, self, self._root)



    class StochiometryInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(4)
            self.element_for_stochiometry = self._root.ElementT(self._io, self, self._root)
            self.n_changed_oxy_states = self._io.read_u4le()
            self.oxy_state_changes = [None] * (self.n_changed_oxy_states)
            for i in range(self.n_changed_oxy_states):
                self.oxy_state_changes[i] = self._root.ElementOxyState(self._io, self, self._root)



    class ImgSetup(KaitaiStruct):
        """this is roughly RE and far from complete."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(12)
            self.n_sub_setups = self._io.read_u4le()
            self.subsetups = [None] * (self.n_sub_setups)
            for i in range(self.n_sub_setups):
                self.subsetups[i] = self._root.SubSetup(self._io, self, self._root)



    class ElementOxyState(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element = self._root.ElementT(self._io, self, self._root)
            self.oxy_state = self._io.read_f4le()


    class QuantiOptions(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.qti_analysis_mode = self._root.AnalysisMode(self._io.read_u4le())
            _on = self.qti_analysis_mode
            if _on == self._root.AnalysisMode.by_stochiometry:
                self.analysis_mode_info = self._root.StochiometryInfo(self._io, self, self._root)
            elif _on == self._root.AnalysisMode.matrix_def_and_stoch:
                self.analysis_mode_info = self._root.MatrixDefinitionAndStochInfo(self._io, self, self._root)
            elif _on == self._root.AnalysisMode.with_matrix_definition:
                self.analysis_mode_info = self._root.MatrixDefinitionInfo(self._io, self, self._root)
            elif _on == self._root.AnalysisMode.by_difference:
                self.analysis_mode_info = self._root.ByDifferenceInfo(self._io, self, self._root)
            elif _on == self._root.AnalysisMode.stoch_and_difference:
                self.analysis_mode_info = self._root.StochAndDifferenceInfo(self._io, self, self._root)
            self.reserved_2 = self._io.read_bytes(12)
            self.matrix_correction_model = self._root.MatrixCorrectionType(self._io.read_u4le())
            self.geo_species_name = self._root.CSharpString(self._io, self, self._root)


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
            self.n_sub_setups = self._io.read_u4le()
            self.subsetups = [None] * (self.n_sub_setups)
            for i in range(self.n_sub_setups):
                self.subsetups[i] = self._root.SubSetup(self._io, self, self._root)

            self.reserved_1 = self._io.read_u4le()
            self.fixed_order = self._io.read_u4le()
            self.reserved_2 = self._io.read_bytes(16)
            self.quantification_options = self._root.QuantiOptions(self._io, self, self._root)
            self.same_line_multi_spect_handling = self._root.MSpectSameLineHandling(self._io.read_u4le())
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
            self.data = self._io.read_bytes(self.data_array_size)
            self.not_re_flag = self._io.read_u4le()
            self.signal_name = self._root.CSharpString(self._io, self, self._root)
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
            self.lut_name = self._root.CSharpString(self._io, self, self._root)
            self.reserved_3 = self._io.read_bytes(52)
            self.n_of_annot_lines = self._io.read_u4le()
            self.annotated_lines_table = [None] * (self.n_of_annot_lines)
            for i in range(self.n_of_annot_lines):
                self.annotated_lines_table[i] = self._root.AnnotatedLines(self._io, self, self._root)

            self.reserved_4 = self._io.read_bytes(4)
            self.n_extra_ending = self._io.read_u4le()
            self.extra_ending = [None] * (self.n_extra_ending)
            for i in range(self.n_extra_ending):
                self.extra_ending[i] = self._root.WdsItemExtraEnding(self._io, self, self._root)



    class MatrixDefinitionAndStochInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(4)
            self.element_for_stochiometry = self._root.ElementT(self._io, self, self._root)
            self.n_changed_oxy_states = self._io.read_u4le()
            self.oxy_state_changes = [None] * (self.n_changed_oxy_states)
            for i in range(self.n_changed_oxy_states):
                self.oxy_state_changes[i] = self._root.ElementOxyState(self._io, self, self._root)

            self.reserved_2 = self._io.read_bytes(4)
            self.n_elements = self._io.read_u4le()
            self.element_table = [None] * (self.n_elements)
            for i in range(self.n_elements):
                self.element_table[i] = self._root.ElementWeight(self._io, self, self._root)



    class WdsQtiSignal(KaitaiStruct):
        def __init__(self, n_points, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.n_points = n_points
            self._read()

        def _read(self):
            self.version = self._io.read_u4le()
            self.dataset_type = self._root.DatasetType(self._io.read_u4le())
            self.data_size = self._io.read_u4le()
            self.data = [None] * (self.n_points)
            for i in range(self.n_points):
                self.data[i] = self._root.QtiDataItem(self._io, self, self._root)

            self.reserved_0 = self._io.read_u4le()
            self.standard_name = self._root.CSharpString(self._io, self, self._root)
            self.n_elements_standard = self._io.read_u4le()
            self.standard_weight_table = [None] * (self.n_elements_standard)
            for i in range(self.n_elements_standard):
                self.standard_weight_table[i] = self._root.ElementWeight(self._io, self, self._root)

            self.calib_hv = self._io.read_f4le()
            self.calib_current = self._io.read_f4le()
            self.i_standard = self._io.read_f4le()
            self.i_standard_std = self._io.read_f4le()
            self.calibration_file_name = self._root.CSharpString(self._io, self, self._root)
            self.calib_peak_time = self._io.read_f4le()
            self.calib_bkgd_time = self._io.read_f4le()
            self.bkgd_1_pos = self._io.read_s4le()
            self.bkgd_2_pos = self._io.read_s4le()
            self.bkgd_slope = self._io.read_f4le()
            self.quanti_mode = self._root.QuantiMode(self._io.read_u4le())
            self.pk_area_range = self._io.read_u4le()
            self.pk_area_channels = self._io.read_u4le()
            self.pk_area_bkgd_1 = self._io.read_s4le()
            self.pk_area_bkgd2 = self._io.read_s4le()
            self.pk_area_n_accumulation = self._io.read_u4le()
            self.not_re_pk_area_flags = self._io.read_bytes(36)
            self.n_of_embedded_wds = self._io.read_u4le()
            self.pk_area_wds_spectras = [None] * (self.n_of_embedded_wds)
            for i in range(self.n_of_embedded_wds):
                self.pk_area_wds_spectras[i] = self._root.QuantiWdsScan(self._io, self, self._root)

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
            self.element = self._root.ElementT(self._io, self, self._root)
            self.line = self._root.XrayLine(self._io.read_u4le())
            self.i_element = self._io.read_u4le()
            self.i_line = self._root.XrayLine(self._io.read_u4le())
            self.i_order = self._io.read_u4le()
            self.i_offset = self._io.read_s4le()
            self.hv = self._io.read_f4le()
            self.beam_current = self._io.read_f4le()
            self.peak_min_bkgd = self._io.read_f4le()
            self.standard_name = self._root.CSharpString(self._io, self, self._root)
            self.nr_in_standard_db = self._io.read_u4le()
            self.spect_nr = self._io.read_u4le()
            self._raw_xtal = self._io.read_bytes(4)
            io = KaitaiStream(BytesIO(self._raw_xtal))
            self.xtal = self._root.XtalT(io, self, self._root)
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
            self.standard_name = self._root.CSharpString(self._io, self, self._root)


    class MatrixDefinitionInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved_0 = self._io.read_bytes(4)
            self.n_elements = self._io.read_u4le()
            self.element_table = [None] * (self.n_elements)
            for i in range(self.n_elements):
                self.element_table[i] = self._root.ElementWeight(self._io, self, self._root)




