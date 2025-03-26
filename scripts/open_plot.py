from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from tree_view.tree_widget import TreeWidget


import pandas as pd

from tree_view.tracks_from_df import tracks_from_df


class MainWindow(QMainWindow):
    def __init__(self, cluster=False):
        super().__init__()

        csv_path = "scripts/hela_example_tracks.csv"
        df = pd.read_csv(csv_path)
        df["time"] = df["t"]

        tracks = tracks_from_df(df, features={"track_id": "track_id", "area": "area"})

        self.tree_widget = TreeWidget(tracks)
        self.setCentralWidget(self.tree_widget)
        #self.setWindowState(Qt.WindowMaximized)


if __name__ == "__main__":
    # You need one (and only one) QApplication instance per application.
    app = QApplication([])

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec()

    # Your application won't reach here until you exit and the event
    # loop has stopped.
