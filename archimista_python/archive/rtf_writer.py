"""
Porting di app/models/rtfwriter.rb — Scrittore RTF low-level.
Genera codice RTF raw per la creazione di documenti .rtf compatibili.
"""

import io
import re

# ──────────────────────────────────────────────────────────────────────────────
# Costanti (da Ruby GCrw*)
# ──────────────────────────────────────────────────────────────────────────────

GCrwStyleNormal = 0
GCrwStyleHeading1 = 1
GCrwStyleHeading2 = 2
GCrwStyleHeading3 = 3
GCrwStyleHeading4 = 4
GCrwStyleHeading5 = 5
GCrwStyleHeading = 6
GCrwStylePredefinedCount = 7
GCrwStyleCurrent = -1

GCrwFontNameTimesNewRoman = 0
GCrwFontNameArial = 1
GCrwFontNameMSSansSerif = 2
GCrwFontNameCourierNew = 3
GCrwFontNameVerdana = 4
GCrwFontNameSymbol = 5
GCrwFontNameCurrent = -1

GCrwFontBoldDisabled = 0
GCrwFontBoldEnabled = 1
GCrwFontBoldCurrent = -1

GCrwFontItalicDisabled = 0
GCrwFontItalicEnabled = 1
GCrwFontItalicCurrent = -1

GCrwFontUnderlinedDisabled = 0
GCrwFontUnderlinedEnabled = 1
GCrwFontUnderlinedCurrent = -1

GCrwTextAlignmentLeft = 0
GCrwTextAlignmentCenter = 1
GCrwTextAlignmentRight = 2
GCrwTextAlignmentJustified = 3
GCrwTextAlignmentCurrent = -1

GCrwTextColorBlack = 0
GCrwTextColorMaroon = 1
GCrwTextColorGreen = 2
GCrwTextColorOlive = 3
GCrwTextColorNavy = 4
GCrwTextColorPurple = 5
GCrwTextColorTeal = 6
GCrwTextColorGray = 7
GCrwTextColorSilver = 8
GCrwTextColorRed = 9
GCrwTextColorLime = 10
GCrwTextColorYellow = 11
GCrwTextColorBlue = 12
GCrwTextColorFuchsia = 13
GCrwTextColorAqua = 14
GCrwTextColorWhite = 15
GCrwTextColorCurrent = -1

GCrwIndentationCMQuarters00 = 0
GCrwIndentationCMQuarters01 = 142
GCrwIndentationCMQuarters02 = 282
GCrwIndentationCMQuarters03 = 426
GCrwIndentationCMQuarters04 = 568
GCrwIndentationCMQuarters05 = 710
GCrwIndentationCMQuarters06 = 852
GCrwIndentationCMQuarters07 = 994
GCrwIndentationCMQuarters08 = 1136
GCrwIndentationCMQuarters09 = 1278
GCrwIndentationCMQuarters10 = 1420
GCrwIndentationCMQuartersCurrent = 10000

GCrwHeaderFooterPageBoth = 0
GCrwHeaderFooterPageLeft = 1
GCrwHeaderFooterPageRight = 2

MC_ALIGNMENT_CHARS = "lcrj"

# Mappatura caratteri ANSI → RTF per caratteri non-ASCII (ISO-8859-1 / cp1252)
ANSI_TO_RTF_REMAP = {
    8364: "'80",  # Euro
    402: "'83",   # florin
    8230: "'85",  # ellipsis
    710: "'88",   # circumflex
    8240: "'89",  # per mille
    8249: "'8b",  # left single angle bracket
    8216: "'91",  # left single quotation mark
    8217: "'92",  # right single quotation mark
    8220: "'93",  # left double quotation mark
    8221: "'94",  # right double quotation mark
    8250: "'9b",  # right single angle bracket
    8211: "-",    # en dash → semplice trattino
}


class RtfWriter:
    """Scrittore RTF low-level. Porting di RtfWriter da Ruby."""

    def __init__(self):
        self._file = None
        self._current_line_indentation_index = 0
        self._current_first_line_indentation_index = 0

    def is_open(self):
        return self._file is not None

    def file_create(self, filename):
        """Apre il file RTF in scrittura (encoding ISO-8859-1)."""
        self._file = open(filename, 'w', encoding='iso-8859-1', errors='replace')

    def file_create_buffer(self):
        """Apre un buffer di scrittura (per generazione in-memory)."""
        self._file = io.StringIO()

    def file_close(self):
        """Chiude il file RTF."""
        if not self.is_open():
            return
        if hasattr(self._file, 'close'):
            self._file.close()
        self._file = None

    def get_output(self):
        """Restituisce il contenuto dal buffer (se usato file_create_buffer)."""
        if self._file and hasattr(self._file, 'getvalue'):
            return self._file.getvalue()
        return ""

    def write_file_head(self, custom_stylesheets=None):
        """Scrive l'intestazione RTF (fonttbl, colortbl, stylesheet)."""
        if not self.is_open():
            return

        self._ascii_file_put_line("{\\rtf1\\ansi \\deff0")

        # Font table
        self._ascii_file_put_line("{\\fonttbl")
        self._ascii_file_put_line("\\f0\\froman Times New Roman;")
        self._ascii_file_put_line("\\f1\\fswiss Arial;")
        self._ascii_file_put_line("\\f2\\fswiss MS Sans Serif;")
        self._ascii_file_put_line("\\f3\\fmodern Courier New;")
        self._ascii_file_put_line("\\f4\\fswiss Verdana;")
        self._ascii_file_put_line("\\f5\\fnil Symbol;")
        self._ascii_file_put_line("}")

        # Color table
        self._ascii_file_put_line("{\\colortbl;")
        self._ascii_file_put_line("\\red127\\green0\\blue0;")    # 1: maroon
        self._ascii_file_put_line("\\red0\\green127\\blue0;")    # 2: green
        self._ascii_file_put_line("\\red127\\green127\\blue0;")  # 3: olive
        self._ascii_file_put_line("\\red0\\green0\\blue127;")    # 4: navy
        self._ascii_file_put_line("\\red127\\green0\\blue127;")  # 5: purple
        self._ascii_file_put_line("\\red0\\green127\\blue127;")  # 6: teal
        self._ascii_file_put_line("\\red127\\green127\\blue127;")# 7: gray
        self._ascii_file_put_line("\\red192\\green192\\blue192;")# 8: silver
        self._ascii_file_put_line("\\red255\\green0\\blue0;")    # 9: red
        self._ascii_file_put_line("\\red0\\green255\\blue0;")    # 10: lime
        self._ascii_file_put_line("\\red255\\green255\\blue0;")  # 11: yellow
        self._ascii_file_put_line("\\red0\\green0\\blue255;")    # 12: blue
        self._ascii_file_put_line("\\red255\\green0\\blue255;")  # 13: fuchsia
        self._ascii_file_put_line("\\red0\\green255\\blue255;")  # 14: aqua
        self._ascii_file_put_line("\\red255\\green255\\blue255;")# 15: white
        self._ascii_file_put_line("}")

        # Stylesheet table
        self._ascii_file_put_line("{\\stylesheet")
        self._ascii_file_put_line("{\\fs24 \\snext0Normal;}")
        self._ascii_file_put_line("{\\s1\\ql\\b\\f0\\fs30 heading 1;}")
        self._ascii_file_put_line("{\\s2\\ql\\b\\f0\\fs28 heading 2;}")
        self._ascii_file_put_line("{\\s3\\ql\\b\\f0\\fs26 heading 3;}")
        self._ascii_file_put_line("{\\s4\\ql\\b\\f0\\fs24 heading 4;}")
        self._ascii_file_put_line("{\\s5\\ql\\b\\f0\\fs22 heading 5;}")
        self._ascii_file_put_line("{\\s6\\ql\\b\\f0\\fs36 Titolo;}")

        if custom_stylesheets:
            for stylesheet in custom_stylesheets:
                self._ascii_file_put_line(stylesheet)

        self._ascii_file_put_line("}")

        # Default font
        self._ascii_file_put_line("\\fs20\\f1")

    def write_file_tail(self):
        """Chiude il documento RTF."""
        if not self.is_open():
            return
        self._ascii_file_put_line("}")

    def write_text(self, par_text, style_index=None, fnt_name_index=None,
                   fnt_size_value=None, fnt_bold_index=None, fnt_italic_index=None,
                   fnt_underlined_index=None, txt_alignment_index=None, txt_color_index=None,
                   line_indentation_index=None, first_line_indentation_index=None):
        """Scrive un testo semplice (senza paragrafo)."""
        if not self.is_open():
            return

        txt_settings = self._create_settings(
            style_index, fnt_name_index, fnt_size_value, fnt_bold_index,
            fnt_italic_index, fnt_underlined_index, txt_alignment_index,
            txt_color_index, line_indentation_index, first_line_indentation_index)

        if txt_settings:
            txt_prefix = "{" + txt_settings + " "
            txt_postfix = "}"
        else:
            txt_prefix = ""
            txt_postfix = ""

        escaped = str(par_text).replace("\\", "\\\\")
        escaped = self._ansi_to_rtf_remap(escaped)
        self._ascii_file_put_line(txt_prefix + escaped + txt_postfix)

    def write_paragraph(self, par_text, style_index=None, fnt_name_index=None,
                        fnt_size_value=None, fnt_bold_index=None, fnt_italic_index=None,
                        fnt_underlined_index=None, txt_alignment_index=None, txt_color_index=None,
                        line_indentation_index=None, first_line_indentation_index=None):
        """Scrive un paragrafo completo con supporto per liste e formattazione inline."""
        if not self.is_open():
            return

        txt_settings = self._create_settings(
            style_index, fnt_name_index, fnt_size_value, fnt_bold_index,
            fnt_italic_index, fnt_underlined_index, txt_alignment_index,
            txt_color_index, line_indentation_index, first_line_indentation_index)

        if txt_settings:
            txt_prefix = "{" + txt_settings + " "
            txt_postfix = "}"
        else:
            txt_prefix = ""
            txt_postfix = ""

        if par_text:
            text_lines = str(par_text).replace("\r\n", "\n").split("\n")
            n = len(text_lines)

            # Process unordered lists (* )
            is_start_tag_unordered = [False] * n
            is_end_tag_unordered = [False] * n
            pc = self._unordered_list_get_point_char()

            self._process_list_markers(
                text_lines, is_start_tag_unordered, is_end_tag_unordered,
                marker="* ", is_unordered=True, pc=pc)

            # Process ordered lists (# )
            is_start_tag_ordered = [False] * n
            is_end_tag_ordered = [False] * n
            self._process_list_markers(
                text_lines, is_start_tag_ordered, is_end_tag_ordered,
                marker="# ", is_unordered=False)

            for index, line in enumerate(text_lines):
                line = line.replace("\\", "\\\\")
                line = self._process_inline_formatting(line)

                if is_start_tag_unordered[index]:
                    self._ascii_file_put_line(self._unordered_list_get_start_tag(pc))
                if is_start_tag_ordered[index]:
                    self._ascii_file_put_line(self._ordered_list_get_start_tag(1))

                self._ascii_file_put_line(txt_prefix + line + "\\par" + txt_postfix)

                if is_end_tag_unordered[index]:
                    self._ascii_file_put_line("\\pard")
                if is_end_tag_ordered[index]:
                    self._ascii_file_put_line("\\pard")
        else:
            self._ascii_file_put_line(txt_prefix + "\\par" + txt_postfix)

    def write_line_separator(self, style_index=None, fnt_name_index=None, fnt_size_value=None):
        """Scrive un separatore orizzontale."""
        if style_index is None:
            style = ""
        else:
            style = f"\\s{style_index}"

        if fnt_name_index is None:
            fnt_name = ""
        else:
            fnt_name = f"\\f{style_index}"

        if fnt_size_value is None:
            fnt_size = "\\fs16"
        else:
            fnt_size = f"\\fs{fnt_size_value}"

        ls = f"{{\\pard \\brdrb \\brdrs\\brdrw10\\brsp20{style} {{{fnt_name}{fnt_size}\\~}}\\par \\pard}}{{\\pard {style}{fnt_name}{fnt_size}\\par \\pard}}"
        self._ascii_file_put_line(ls)

    def write_new_page(self):
        """Salta a una nuova pagina."""
        if not self.is_open():
            return
        self._ascii_file_put_line("\\page")

    def write_new_line(self, style_index=None, fnt_name_index=None, fnt_size_value=None,
                       fnt_bold_index=None, fnt_italic_index=None, fnt_underlined_index=None,
                       txt_alignment_index=None, txt_color_index=None,
                       line_indentation_index=None, first_line_indentation_index=None):
        """Scrive una riga vuota."""
        self.write_paragraph(
            "", style_index, fnt_name_index, fnt_size_value, fnt_bold_index,
            fnt_italic_index, fnt_underlined_index, txt_alignment_index,
            txt_color_index, line_indentation_index, first_line_indentation_index)

    def write_header(self, hdr_text, style_index=None, fnt_name_index=None,
                     fnt_size_value=None, fnt_bold_index=None, fnt_italic_index=None,
                     fnt_underlined_index=None, txt_alignment_index=None, txt_color_index=None,
                     line_indentation_index=None, first_line_indentation_index=None,
                     page_target=None):
        """Scrive l'header di pagina."""
        if not self.is_open():
            return
        if page_target is None:
            page_target = GCrwHeaderFooterPageBoth

        txt_settings = self._create_settings(
            style_index, fnt_name_index, fnt_size_value, fnt_bold_index,
            fnt_italic_index, fnt_underlined_index, txt_alignment_index,
            txt_color_index, line_indentation_index, first_line_indentation_index)

        if txt_settings:
            txt_prefix = txt_settings + " {"
            txt_postfix = "}"
        else:
            txt_prefix = "{"
            txt_postfix = "}"

        pt = ""
        if page_target == GCrwHeaderFooterPageLeft:
            pt = "l"
        elif page_target == GCrwHeaderFooterPageRight:
            pt = "r"

        self._ascii_file_put_line(f"{{\\header{pt} {txt_prefix}{hdr_text}{txt_postfix}{{\\par}}}}")

    def write_footer(self, ftr_text, style_index=None, fnt_name_index=None,
                     fnt_size_value=None, fnt_bold_index=None, fnt_italic_index=None,
                     fnt_underlined_index=None, txt_alignment_index=None, txt_color_index=None,
                     line_indentation_index=None, first_line_indentation_index=None,
                     page_target=None):
        """Scrive il footer di pagina."""
        if not self.is_open():
            return
        if page_target is None:
            page_target = GCrwHeaderFooterPageBoth

        txt_settings = self._create_settings(
            style_index, fnt_name_index, fnt_size_value, fnt_bold_index,
            fnt_italic_index, fnt_underlined_index, txt_alignment_index,
            txt_color_index, line_indentation_index, first_line_indentation_index)

        if txt_settings:
            txt_prefix = txt_settings + " {"
            txt_postfix = "}"
        else:
            txt_prefix = "{"
            txt_postfix = "}"

        tmp_ftr_text = ftr_text
        tmp_ftr_text = tmp_ftr_text.replace("%PAGE%", "{\\field{\\*\\fldinst { PAGE }}}")
        tmp_ftr_text = tmp_ftr_text.replace("%NUMPAGES%", "{\\field{\\*\\fldinst { NUMPAGES }}}")

        pt = ""
        if page_target == GCrwHeaderFooterPageLeft:
            pt = "l"
        elif page_target == GCrwHeaderFooterPageRight:
            pt = "r"

        self._ascii_file_put_line(f"{{\\footer{pt} {txt_prefix}{tmp_ftr_text}{txt_postfix}{{\\par}}}}")

    def write_raw(self, txt):
        """Scrive testo RTF raw senza escaping."""
        if not self.is_open():
            return
        self._ascii_file_put_line(txt)

    def write_settings(self, style_index=None, fnt_name_index=None, fnt_size_value=None,
                       fnt_bold_index=None, fnt_italic_index=None, fnt_underlined_index=None,
                       txt_alignment_index=None, txt_color_index=None,
                       line_indentation_index=None, first_line_indentation_index=None):
        """Scrive le impostazioni di stile correnti."""
        if not self.is_open():
            return

        txt_settings = self._create_settings(
            style_index, fnt_name_index, fnt_size_value, fnt_bold_index,
            fnt_italic_index, fnt_underlined_index, txt_alignment_index,
            txt_color_index, line_indentation_index, first_line_indentation_index)

        self._ascii_file_put_line(txt_settings)
        self._set_indentation(line_indentation_index, first_line_indentation_index)

    # ──────────────────────────────────────────────────────────────────────
    # List helpers
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _unordered_list_get_point_char(point_char=None):
        if point_char is None:
            return "\\'B7"  # bullet character
        return "\\f0 " + point_char

    @staticmethod
    def _unordered_list_get_start_tag(rtf_point_char):
        return f"\\pard\n{{\\*\\pn\\pnlvlblt\\pnf5\\pnindent0{{\\pntxtb{rtf_point_char}}}}}\\fi-284\\li284"

    @staticmethod
    def _unordered_list_get_item(item_text, rtf_point_char):
        return f"{{\\pntext{rtf_point_char}\\tab}}" + item_text

    @staticmethod
    def _ordered_list_get_start_tag(start_index):
        return f"\\pard\n{{\\*\\pn\\pnlvlbody\\pnf0\\pnindent0\\pnstart{start_index}\\pndec{{\\pntxta.}}}}\\fi-284\\li284"

    @staticmethod
    def _ordered_list_get_item(item_text, item_index):
        return f"{{\\pntext\\f0 {item_index}.\\tab}}" + item_text

    # ──────────────────────────────────────────────────────────────────────
    # Private methods
    # ──────────────────────────────────────────────────────────────────────

    def _ascii_file_put_line(self, txt_line):
        """Scrive una riga nel file RTF."""
        if not self.is_open():
            return
        try:
            self._file.write(txt_line + "\n")
        except Exception:
            try:
                wrk_txt_line = self._ansi_to_rtf_remap(txt_line)
                self._file.write(wrk_txt_line + "\n")
            except Exception:
                pass

    def _create_settings(self, style_index, fnt_name_index, fnt_size_value,
                         fnt_bold_index, fnt_italic_index, fnt_underlined_index,
                         txt_alignment_index, txt_color_index,
                         indentation_index, first_line_indentation_index):
        """Crea la stringa di impostazioni RTF."""
        txt_settings = ""

        if style_index is None:
            style_index = GCrwStyleCurrent
        if fnt_name_index is None:
            fnt_name_index = GCrwFontNameCurrent
        if fnt_size_value is None:
            fnt_size_value = 0
        if fnt_bold_index is None:
            fnt_bold_index = GCrwFontBoldCurrent
        if fnt_italic_index is None:
            fnt_italic_index = GCrwFontItalicCurrent
        if fnt_underlined_index is None:
            fnt_underlined_index = GCrwFontUnderlinedCurrent
        if txt_alignment_index is None:
            txt_alignment_index = GCrwTextAlignmentCurrent
        if txt_color_index is None:
            txt_color_index = GCrwTextColorCurrent
        if indentation_index is None:
            indentation_index = GCrwIndentationCMQuartersCurrent
        if first_line_indentation_index is None:
            first_line_indentation_index = GCrwIndentationCMQuartersCurrent

        if style_index != GCrwStyleCurrent:
            txt_settings += f"\\s{style_index}"
        if fnt_name_index != GCrwFontNameCurrent:
            if fnt_name_index >= 0:
                txt_settings += f"\\f{fnt_name_index}"
            else:
                fnt_name_index = GCrwFontNameCurrent - 1 + (fnt_name_index * -1)
                txt_settings += f"\\f{fnt_name_index}"
        if fnt_size_value != 0:
            txt_settings += f"\\fs{fnt_size_value * 2}"
        if fnt_bold_index != GCrwFontBoldCurrent:
            txt_settings += f"\\b{fnt_bold_index}"
        if fnt_italic_index != GCrwFontItalicCurrent:
            txt_settings += f"\\i{fnt_italic_index}"
        if fnt_underlined_index != GCrwFontUnderlinedCurrent:
            txt_settings += f"\\ul{fnt_underlined_index}"
        if txt_alignment_index != GCrwTextAlignmentCurrent:
            txt_settings += f"\\q{MC_ALIGNMENT_CHARS[txt_alignment_index]}"
        if txt_color_index != GCrwTextColorCurrent:
            if txt_color_index >= 0:
                txt_settings += f"\\cf{txt_color_index}"
            else:
                txt_color_index = GCrwTextColorCurrent - 1 + (txt_color_index * -1)
                txt_settings += f"\\cf{txt_color_index}"
        if indentation_index != GCrwIndentationCMQuartersCurrent:
            txt_settings += f"\\li{indentation_index}"
        if first_line_indentation_index != GCrwIndentationCMQuartersCurrent:
            txt_settings += f"\\fi{first_line_indentation_index}"

        return txt_settings

    def _set_indentation(self, line_indentation_index, first_line_indentation_index):
        if line_indentation_index != GCrwIndentationCMQuartersCurrent:
            self._current_line_indentation_index = line_indentation_index
        if first_line_indentation_index != GCrwIndentationCMQuartersCurrent:
            self._current_first_line_indentation_index = first_line_indentation_index

    def _ansi_to_rtf_remap(self, ip_str):
        """Converte caratteri non-ASCII in escape RTF."""
        op_str = ""
        for c in ip_str:
            code = ord(c)
            if code < 128:
                op_str += c
            else:
                if code in ANSI_TO_RTF_REMAP:
                    op_str += f"\\{ANSI_TO_RTF_REMAP[code]}"
                else:
                    op_str += f"\\'{code:02x}"
        return op_str

    def _process_inline_formatting(self, line):
        """Gestisce la formattazione inline: *bold*, _italic_."""
        # Italic: _text_
        if line.startswith("_") or " _" in line:
            line = " " + line + " "
            while " _" in line and "_ " in line:
                line = line.replace(" _", " \\i1 ", 1)
                line = line.replace("_ ", "\\i0  ", 1)
            line = line[1:-1] if line.startswith(" ") and line.endswith(" ") else line

        # Bold: *text*
        if line.startswith("*") or " *" in line:
            line = " " + line + " "
            while " *" in line and "* " in line:
                line = line.replace(" *", " \\b1 ", 1)
                line = line.replace("* ", "\\b0  ", 1)
            line = line[1:-1] if line.startswith(" ") and line.endswith(" ") else line

        return line

    def _process_list_markers(self, text_lines, is_start_tag, is_end_tag, marker, is_unordered=True, pc=None):
        """Processa le linee con marker di lista (* per unordered, # per ordered)."""
        n = len(text_lines)
        pos_from = -1
        pos_to = -1

        for index in range(n):
            line = text_lines[index]
            if len(line) >= 2 and line[:2] == marker:
                if pos_from == -1:
                    pos_from = index
            else:
                if pos_from >= 0:
                    pos_to = index - 1

            if pos_from >= 0 and pos_to == -1 and index == n - 1:
                pos_to = index

            if pos_from >= 0 and pos_to >= 0:
                if is_unordered:
                    s = text_lines[pos_from]
                    if len(s) >= 2:
                        s = s[2:]
                    text_lines[pos_from] = self._unordered_list_get_item(s, pc)
                    is_start_tag[pos_from] = True

                    if pos_from + 1 <= pos_to - 1:
                        for i in range(pos_from + 1, pos_to):
                            s = text_lines[i]
                            if len(s) >= 2:
                                s = s[2:]
                            text_lines[i] = self._unordered_list_get_item(s, pc)
                            is_start_tag[i] = False  # Not start, just middle

                    if pos_to > pos_from:
                        s = text_lines[pos_to]
                        if len(s) >= 2:
                            s = s[2:]
                        text_lines[pos_to] = self._unordered_list_get_item(s, pc)
                    is_end_tag[pos_to] = True
                else:
                    # Ordered list
                    j = 1
                    s = text_lines[pos_from]
                    if len(s) >= 2:
                        s = s[2:]
                    text_lines[pos_from] = self._ordered_list_get_item(s, j)
                    is_start_tag[pos_from] = True
                    j += 1

                    if pos_from + 1 <= pos_to - 1:
                        for i in range(pos_from + 1, pos_to):
                            s = text_lines[i]
                            if len(s) >= 2:
                                s = s[2:]
                            text_lines[i] = self._ordered_list_get_item(s, j)
                            is_start_tag[i] = False
                            j += 1

                    if pos_to > pos_from:
                        s = text_lines[pos_to]
                        if len(s) >= 2:
                            s = s[2:]
                        text_lines[pos_to] = self._ordered_list_get_item(s, j)
                    is_end_tag[pos_to] = True

                pos_from = -1
                pos_to = -1
