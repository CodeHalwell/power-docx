
.. _text_api:

Text-related objects
====================


|Paragraph| objects
-------------------

.. autoclass:: power_docx.text.paragraph.Paragraph()
   :members:


|ParagraphFormat| objects
-------------------------

.. autoclass:: power_docx.text.parfmt.ParagraphFormat()
   :members:


|Hyperlink| objects
-------------------

.. autoclass:: power_docx.text.hyperlink.Hyperlink()
   :members:


|Run| objects
-------------

.. autoclass:: power_docx.text.run.Run()
   :members:


|Font| objects
--------------

.. autoclass:: power_docx.text.run.Font()
   :members:


|RenderedPageBreak| objects
---------------------------

.. autoclass:: power_docx.text.pagebreak.RenderedPageBreak()
   :members:


|TabStop| objects
-----------------

.. autoclass:: power_docx.text.tabstops.TabStop()
   :members:


|TabStops| objects
------------------

.. autoclass:: power_docx.text.tabstops.TabStops()
   :members: clear_all

   .. automethod:: power_docx.text.tabstops.TabStops.add_tab_stop(position, alignment=WD_TAB_ALIGNMENT.LEFT, leader=WD_TAB_LEADER.SPACES)
