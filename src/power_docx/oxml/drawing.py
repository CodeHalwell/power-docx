"""Custom element-classes for DrawingML-related elements like `<w:drawing>`.

For legacy reasons, many DrawingML-related elements are in `power_docx.oxml.shape`. Expect
those to move over here as we have reason to touch them.
"""

from power_docx.oxml.xmlchemy import BaseOxmlElement


class CT_Drawing(BaseOxmlElement):
    """`<w:drawing>` element, containing a DrawingML object like a picture or chart."""
