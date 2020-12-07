General info:
This is small server to do simple analysis of 2d images, which can be taken from the other Tango server, e.g. TTTGW or VimbaViewer.

The server is better to use with the CameraViewer utility.

Installation:
To start server the 4 parameters has to be provided:

"CameraDevice" - the tango address of image source
The following settings are needed to work with CameraViewer, which update them automatically during start. In case you use server without CameraViewer better to set it to False (or 0) to avoid confusions.

"Flip_H" - define whether the source picture has to be flipped horizontally. Could be True or False.
"Flip_V" -  define whether the source picture has to be flipped vertically. Could be True or False.
"Rotate_Angle" - define the rotation angle in 90 deg steps (!!). E.g. Rotate_Angle = 3 means 270 deg rotation
Operation:
The analysis is performed in the rectangle, defined by roi_x, roi_y, roi_w, roi_h attributes. In case if the roi_w, roi_h are 0 - the whole picture is analyzed.

The following parameters are calculated:

sum - sum of intensities
max_intensity - the maximum value
max_x, max_y - position of center of mass
com_x, com_y - position of center of mass
fwhm_x, fwhm_y - horizontal and vertical size of half maximum of peak
Connection to Sardana:
The server has a variable "value" attribute, which can act as a source for the Sardana scans.

The parameter, which should be passed to "value", selected by "scan_parameter" attribute. It could be: "max_i", "max_x", "max_y", "com_x", "com_y", "fwhm_x", "fwhm_y", "sum"

This is the example of entry to the online.xml, to add server to nxselector :

<device>
<name>lm4_value</name>
<type>counter</type>
<module>tangoattributectctrl</module>
<device>p23/lmanalysis/lm4/value</device>
<control>tango</control>
<hostname>hasep23oh:10000</hostname>
</device>