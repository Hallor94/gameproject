# actions/contextual_action.py

class ContextualAction:
    def __init__(self, action_id, label, callback, icon=None, visible=True):
        """
        Represents an action available at a tile.

        :param action_id: unique string identifier (e.g., 'loot_crate')
        :param label: display text for the menu (e.g., 'Loot Crate')
        :param callback: function to execute when action is triggered
        :param icon: optional icon path or surface
        :param visible: optional bool or callable to determine visibility
        """
        self.id = action_id
        self.label = label
        self.callback = callback
        self.icon = icon
        self.visible = visible

    def is_visible(self, context=None):
        if callable(self.visible):
            return self.visible(context)
        return self.visible
