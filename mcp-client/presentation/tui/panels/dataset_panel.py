"""
Dataset Panel Component
Displays available datasets in the sidebar
"""
from typing import List, Union
from textual.widgets import Static
from textual.containers import VerticalScroll
from textual.app import ComposeResult


class DatasetPanel(VerticalScroll):
    """Panel lateral para datasets"""
    
    # Prevent this panel from taking focus
    can_focus = False

    def compose(self) -> ComposeResult:
        yield Static("## 📊 Datasets\n\nNo datasets loaded", id="dataset-content")

    async def update_datasets(self, datasets: Union[str, List[str]]):
        """Update the datasets display
        
        Args:
            datasets: Either a string with formatted text or a list of dataset names
        """
        content_widget = self.query_one("#dataset-content", Static)
        
        # If it's a string, use it directly
        if isinstance(datasets, str):
            content_widget.update(datasets)
        # If it's a list, format it
        elif isinstance(datasets, list):
            if not datasets:
                content_widget.update("## 📊 Datasets\n\nNo datasets loaded")
            else:
                datasets_text = "## 📊 Datasets\n\n"
                for i, dataset in enumerate(datasets, 1):
                    datasets_text += f"{i}. {dataset}\n"
                content_widget.update(datasets_text)
        else:
            content_widget.update("## 📊 Datasets\n\nNo datasets loaded")
