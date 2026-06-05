class LayoutRegistry:
    layouts = {}

    def __init__(self, layouts=None):
        if layouts is None:
            layouts = []
        for layout in layouts:
            self.add_layout(layout)
        # END LOOP

    # END __init__

    def add_layout(self, layout):
        self.layouts[layout.get_name()] = layout

    # END add_layout

    def get_layout(self, name):
        return self.layouts.get(name)

    # END get_layout

    def get_layout_names(self):
        return self.layouts.keys()

    # END get_layout_names


# END LayoutRegistry
