#### Images in ReadTheDocs Content

Arches displays help-oriented images/gifs in two main locations: the in-app help panels, and the ReadTheDocs documentation. In order to minimize the possibility of duplicate images (or old content), **all** image files are now stored either in `arches/app/media/img/help/` (for those in the in-app help) or `arches/app/media/img/help/rtd/` (for ReadTheDocs specific content).

To include an image in the readthedocs `.txt` content, use the following patterns:

* if the image is also used in the in-app help panels

    ```
    .. image:: ../arches/app/media/img/help/file-name.png
    ```

* if the image only appears in readthedocs content

    ```
    .. image:: ../arches/app/media/img/help/rtd/file-name.png
    ```