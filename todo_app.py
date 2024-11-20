from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, Container
from textual.message import Message
from textual.widgets import Footer, Header, Label, Input, Static, ListView, ListItem, Checkbox, Button


class TodoItem:
    def __init__(self, title: str, completed: bool = False):
        self.title = title
        self.completed = completed

    def toggle(self):
        self.completed = not self.completed

class TodoListItemWidget(Static):
    class DeleteClicked(Message):
        def __init__(self, widget: 'TodoListItemWidget', item: TodoItem):
            super().__init__()
            self.widget = widget
            self.item = item

    class ToggleClicked(Message):
        def __init__(self, widget: 'TodoListItemWidget', item: TodoItem, value: bool):
            super().__init__()
            self.widget = widget
            self.item = item
            self.value = value
            
    DEFAULT_CSS = """
    .todo-list-item-widget__container-right {
        align: right middle;
    }
    
    .todo-list-item-widget__container {
        layout: horizontal;
        height: auto;
        align: left middle;
    }
    
    .todo-list-item-widget__container > Checkbox {
        background: transparent;
        border: none;
        padding: 1;
        margin-right: 1;
    }
    """

    def __init__(self, item: TodoItem):
        super().__init__()
        self.item = item

    def compose(self) -> ComposeResult:
        with Container(classes="todo-list-item-widget__container"):
            yield Checkbox(self.item.title, value=self.item.completed)
            with HorizontalGroup(classes="todo-list-item-widget__container-right"):
                yield Button("⌫ Delete", variant="warning", classes="todo-list-item-widget__delete-button")

    def on_button_pressed(self):
        self.post_message(TodoListItemWidget.DeleteClicked(self, self.item))
        
    def on_checkbox_changed(self, message: Checkbox.Changed):
        self.post_message(TodoListItemWidget.ToggleClicked(self, self.item, message.value))

    def handle_item_update(self):
        self.query_one(Checkbox).value = self.item.completed


class TodoListWidget(Static):
    DEFAULT_CSS = """
    ListView {
        height: auto;
    }
    """
    initial_items: list[TodoItem]

    def __init__(self, initial_items: list[TodoItem]):
        super().__init__()
        self.initial_items = initial_items
        
    def compose(self) -> ComposeResult:
        list_items: list[ListItem] = list(map(lambda item: ListItem(TodoListItemWidget(item)), self.initial_items))
        yield ListView(*list_items)

    def remove_item(self, item_index: int):
        self.query_one(ListView).remove_items([item_index])
        
    def add_item(self, item: TodoItem):
        self.query_one(ListView).append(ListItem(TodoListItemWidget(item)))

class TodoApp(App):
    BINDINGS = [
        ("ctrl+q", "exit", "Exit"),
    ]

    def __init__(self):
        super().__init__()
        # TODO Load items from a file
        self.items: list[TodoItem] = [TodoItem("Item 1"), TodoItem("Item 2", completed=True), TodoItem("Item 3")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input("", tooltip="This is a tooltip", placeholder="What needs to be done?")
        yield TodoListWidget(self.items[:])
        yield Label("", variant="primary")
        yield Footer()

    def action_exit(self):
        self.exit()
        
    def on_input_submitted(self, message: Input.Submitted):
        new_item = TodoItem(message.value)
        self.items.append(new_item)
        self.query_one(TodoListWidget).add_item(new_item)
        message.input.clear()

    def on_todo_list_item_widget_delete_clicked(self, message: TodoListItemWidget.DeleteClicked):
        index = self.items.index(message.item)
        self.items.remove(message.item)
        self.query_one(TodoListWidget).remove_item(index)
        # TODO Persist changes 
        
    def on_todo_list_item_widget_toggle_clicked(self, message: TodoListItemWidget.ToggleClicked):
        message.item.toggle()
        message.widget.handle_item_update()
        # TODO Persist changes


if __name__ == "__main__":
    TodoApp().run()
