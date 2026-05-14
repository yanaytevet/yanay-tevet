import io

import xlsxwriter

from common.xlsx_generator.table_header_schema import TableHeaderSchema


class XlsxGenerator:
    def __init__(self, headers: list[TableHeaderSchema]):
        self.headers = headers
        self.rows: list[dict] = []

    def add_row(self, row_data: dict) -> None:
        self.rows.append(row_data)

    def get_content(self) -> bytes:
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1,
            'align': 'center',
        })

        max_lengths = {}
        for col_idx, header in enumerate(self.headers):
            max_lengths[col_idx] = len(header.title)
            worksheet.write(0, col_idx, header.title, header_format)

        for row_idx, row_data in enumerate(self.rows, start=1):
            for col_idx, header in enumerate(self.headers):
                value = row_data.get(header.key, "")
                worksheet.write(row_idx, col_idx, value)

                str_value = str(value) if value is not None else ""
                max_lengths[col_idx] = max(max_lengths[col_idx], len(str_value))

        for col_idx, max_length in max_lengths.items():
            width = min(max(max_length * 1.2, 10), 50)
            worksheet.set_column(col_idx, col_idx, width)

        workbook.close()
        output.seek(0)
        return output.getvalue()
