# Click Track Generator by Andrew Pelton
# Created for FPC worship team
# Dec 2024

from import_export import IO
from audio import Click

c = Click()
t = IO.import_track("test.json")
IO.export_track(t, c, 0)