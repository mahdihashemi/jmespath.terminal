import urwid
import jmespath
import json
import argparse


SAMPLE_JSON = {
    'a': 'foo',
    'b': 'bar',
    'c': {
        'd': 'baz',
        'e': [1,2,3]
    }
}



class JMESPathDisplay(object):
    PALETTE = [
        ('input expr', 'bold', ''),
        ('bigtext',      'white',      'black'),
    ]

    def __init__(self, input_data):
        self.view = None
        self.parsed_json = input_data

    def _get_font_instance(self):
        return urwid.get_all_fonts()[-2][1]()

    def _create_view(self):
        self.input_expr = urwid.Edit(('input expr', "JMESPath Expression: "))

        sb = urwid.BigText("JMESPath", self._get_font_instance())
        sb = urwid.Padding(sb, 'center', None)
        sb = urwid.AttrWrap(sb, 'bigtext')
        sb = urwid.Filler(sb, 'top', None, 5)
        self.status_bar = urwid.BoxAdapter(sb, 5)

        div = urwid.Divider()
        self.header = urwid.Pile([self.status_bar, self.input_expr, div, div],
                                 focus_item=1)
        urwid.connect_signal(self.input_expr, 'change', self._on_edit)

        self.input_json = urwid.Text(json.dumps(self.parsed_json, indent=2))
        self.section_title = urwid.Text("Input JSON")
        self.input_json_list = [self.section_title, div, self.input_json]
        self.left_content = urwid.ListBox(self.input_json_list)

        self.right_side_title = urwid.Text("JMESPath result")
        self.jmespath_result = urwid.Text("")
        self.jmespath_result_list = [self.right_side_title, div,
                                     self.jmespath_result]
        self.right_content = urwid.ListBox(self.jmespath_result_list)

        self.content = urwid.Columns([self.left_content, self.right_content])

        self.footer = urwid.Text("Status: ")
        self.view = urwid.Frame(body=self.content, header=self.header,
                                footer=self.footer, focus_part='header')

    def _on_edit(self, widget, text):
        try:
            parsed = jmespath.compile(text)
            self.footer.set_text("Status: success")
        except Exception:
            pass
        else:
            result = parsed.search(self.parsed_json)
            if result is not None:
                self.jmespath_result.set_text(json.dumps(result, indent=2))

    def main(self):
        self._create_view()
        self.loop = urwid.MainLoop(self.view, self.PALETTE,
                                   unhandled_input=self.unhandled_input)
        self.loop.screen.set_terminal_properties(colors=256)
        self.loop.run()

    def unhandled_input(self, key):
        if key == 'f5':
            raise urwid.ExitMainLoop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-json', help='The initial input JSON file to use.')

    args = parser.parse_args()
    if args.input_json is not None:
        input_json = json.load(open(args.input_json))
    else:
        input_json = SAMPLE_JSON

    display = JMESPathDisplay(input_json)
    display.main()


if __name__ == '__main__':
    main()
