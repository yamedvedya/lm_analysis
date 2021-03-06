#!/usr/bin/env python
# -*- coding:utf-8 -*-


# ############################################################################
#  license :
# ============================================================================
#
#  File :        LMAnalysis.py
#
#  Project :     LMAnalysis
#
# This file is part of Tango device class.
# 
# Tango is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Tango is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Tango.  If not, see <http://www.gnu.org/licenses/>.
# 
#
#  $Author :      yury.matveev$
#
#  $Revision :    $
#
#  $Date :        $
#
#  $HeadUrl :     $
# ============================================================================
#            This file is generated by POGO
#     (Program Obviously used to Generate tango Object)
# ############################################################################

__all__ = ["LMAnalysis", "LMAnalysisClass", "main"]

__docformat__ = 'restructuredtext'

import PyTango
import sys
# Add additional import
#----- PROTECTED REGION ID(LMAnalysis.additionnal_import) ENABLED START -----#

import numpy as np
import scipy.ndimage.measurements as scipymeasure
import time
from threading import Thread
from tango import DevState


POLL_PERIOD = 200

# ----------------------------------------------------------------------
def FWHM(array):
    try:
        half_max = (np.amax(array) - np.amin(array)) / 2
        diff = np.sign(array - half_max)
        left_idx = np.where(diff > 0)[0][0]
        right_idx = np.where(diff > 0)[0][-1]
        return right_idx - left_idx
    except:
        return 0

# ----------------------------------------------------------------------
class TangoTineCamera(object):
    """Proxy to a physical TANGO camera.
    """

    # ----------------------------------------------------------------------
    def __init__(self, tango_server, roi):
        super(TangoTineCamera, self).__init__()

        self._last_frame = np.zeros((1, 1))
        self._roi = roi

        self._eid = None
        self._state = 'idle'

        self._last_refresh = time.time()

        self.max_i = 0
        self.max_x = 0
        self.max_y = 0
        self.com_x = 0
        self.com_y = 0
        self.fwhm_x = 0
        self.fwhm_y = 0
        self.sum = 0

        try:
            self.device_proxy = PyTango.DeviceProxy(str(tango_server))
        except:
            self.device_proxy = None

    # ----------------------------------------------------------------------
    def set_new_roi(self, roi):
        self._roi = roi

    # ----------------------------------------------------------------------
    def start(self):

        if not self.device_proxy.is_attribute_polled('Frame'):
            self.device_proxy.poll_attribute('Frame', POLL_PERIOD)
        else:
            if not self.device_proxy.get_attribute_poll_period("Frame") == POLL_PERIOD:
                self.device_proxy.stop_poll_attribute("Frame")
                self.device_proxy.poll_attribute('Frame', POLL_PERIOD)

        self._eid = self.device_proxy.subscribe_event("Frame", PyTango.EventType.PERIODIC_EVENT, self._readoutFrame)

        self._state = 'running'

    # ----------------------------------------------------------------------
    def stop(self):

        if self._eid is not None:
            self.device_proxy.unsubscribe_event(self._eid)

        self._state = 'idle'

    # ----------------------------------------------------------------------
    def _readoutFrame(self, event):
        """Called each time new frame is available.
        """
        data = event.device.read_attribute(event.attr_name.split('/')[6])
        self._last_frame = np.transpose(data.value)
        self._rotate()
        self._analyse_image()
        self._last_refresh = time.time()

    # ----------------------------------------------------------------------
    def _analyse_image(self):

        if self._roi is not None:
            try:
                x, y, w, h, = self._roi
                roi_array = self._last_frame[x:x + w, y:y + h]
            except Exception as err:
                roi_array = self._last_frame
                x, y = 0, 0
        else:
            roi_array = self._last_frame
            x, y = 0, 0

        self.sum = np.sum(roi_array)

        try:
            roi_extrema = scipymeasure.extrema(roi_array)
        except Exception as err:
            roi_extrema = (0, 0, (0, 0), (0, 0))
        self.max_i = roi_extrema[1]
        self.max_x = roi_extrema[3][0] + x
        self.max_y = roi_extrema[3][1] + y

        try:
            roi_com = scipymeasure.center_of_mass(roi_array)
        except Exception as err:
            roi_com = (0, 0)

        self.com_x = roi_com[0] + x
        self.com_y = roi_com[1] + y

        self.fwhm_x = FWHM(np.sum(roi_array, axis=0))
        self.fwhm_y = FWHM(np.sum(roi_array, axis=1))

    # ----------------------------------------------------------------------
    def _read_frame(self):
        self._last_frame = np.transpose(self.device_proxy.Frame)
        self._analyse_image()
        self._last_refresh = time.time()

    # ----------------------------------------------------------------------
    def get_data(self, attr):
        if self._state != 'running' and time.time() - self._last_refresh > POLL_PERIOD/1000:
            self._read_frame()

        return getattr(self, attr)

#----- PROTECTED REGION END -----#	//	LMAnalysis.additionnal_import

# Device States Description
# ON : Server is ready
# OFF : 
# FAULT : 


class LMAnalysis (PyTango.Device_4Impl):
    """"""
    
    # -------- Add you global variables here --------------------------
    #----- PROTECTED REGION ID(LMAnalysis.global_variables) ENABLED START -----#
    
    #----- PROTECTED REGION END -----#	//	LMAnalysis.global_variables

    def __init__(self, cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)
        self.debug_stream("In __init__()")
        LMAnalysis.init_device(self)
        #----- PROTECTED REGION ID(LMAnalysis.__init__) ENABLED START -----#
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.__init__
        
    def delete_device(self):
        self.debug_stream("In delete_device()")
        #----- PROTECTED REGION ID(LMAnalysis.delete_device) ENABLED START -----#
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.delete_device

    def init_device(self):
        self.debug_stream("In init_device()")
        self.get_device_properties(self.get_device_class())
        self.attr_max_x_read = 0.0
        self.attr_max_y_read = 0.0
        self.attr_max_intensity_read = 0.0
        self.attr_com_x_read = 0.0
        self.attr_com_y_read = 0.0
        self.attr_fwhm_x_read = 0.0
        self.attr_fwhm_y_read = 0.0
        self.attr_roi_sum_read = 0.0
        self.attr_scan_parameter_read = ""
        self.attr_value_read = 0.0
        self.attr_roi_x_read = 0
        self.attr_roi_y_read = 0.0
        self.attr_roi_w_read = 0.0
        self.attr_roi_h_read = 0.0
        #----- PROTECTED REGION ID(LMAnalysis.init_device) ENABLED START -----#

        self.camera = TangoTineCamera(self.CameraDevice, None
                                      )
        if self.camera.device_proxy is None:
            self.set_state(DevState.FAULT)
        else:
            self.set_state(DevState.ON)

        self._refresh_thread = Thread(target=self._refresh_data)
        self._refresh_thread_state = 'stopped'


        #----- PROTECTED REGION END -----#	//	LMAnalysis.init_device

    def always_executed_hook(self):
        self.debug_stream("In always_excuted_hook()")
        #----- PROTECTED REGION ID(LMAnalysis.always_executed_hook) ENABLED START -----#
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.always_executed_hook

    # -------------------------------------------------------------------------
    #    LMAnalysis read/write attribute methods
    # -------------------------------------------------------------------------
    
    def read_max_x(self, attr):
        self.debug_stream("In read_max_x()")
        #----- PROTECTED REGION ID(LMAnalysis.max_x_read) ENABLED START -----#
        self.attr_max_x_read = self.camera.get_data('max_x')
        attr.set_value(self.attr_max_x_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.max_x_read
        
    def read_max_y(self, attr):
        self.debug_stream("In read_max_y()")
        #----- PROTECTED REGION ID(LMAnalysis.max_y_read) ENABLED START -----#
        self.attr_max_y_read = self.camera.get_data('max_y')
        attr.set_value(self.attr_max_y_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.max_y_read
        
    def read_max_intensity(self, attr):
        self.debug_stream("In read_max_intensity()")
        #----- PROTECTED REGION ID(LMAnalysis.max_intensity_read) ENABLED START -----#
        self.attr_max_intensity_read = self.camera.get_data('max_i')
        attr.set_value(self.attr_max_intensity_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.max_intensity_read
        
    def read_com_x(self, attr):
        self.debug_stream("In read_com_x()")
        #----- PROTECTED REGION ID(LMAnalysis.com_x_read) ENABLED START -----#
        self.attr_com_x_read = self.camera.get_data('com_x')
        attr.set_value(self.attr_com_x_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.com_x_read
        
    def read_com_y(self, attr):
        self.debug_stream("In read_com_y()")
        #----- PROTECTED REGION ID(LMAnalysis.com_y_read) ENABLED START -----#
        self.attr_com_y_read = self.camera.get_data('com_y')
        attr.set_value(self.attr_com_y_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.com_y_read
        
    def read_fwhm_x(self, attr):
        self.debug_stream("In read_fwhm_x()")
        #----- PROTECTED REGION ID(LMAnalysis.fwhm_x_read) ENABLED START -----#
        self.attr_fwhm_x_read = self.camera.get_data('fwhm_x')
        attr.set_value(self.attr_fwhm_x_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.fwhm_x_read
        
    def read_fwhm_y(self, attr):
        self.debug_stream("In read_fwhm_y()")
        #----- PROTECTED REGION ID(LMAnalysis.fwhm_y_read) ENABLED START -----#
        self.attr_fwhm_y_read = self.camera.get_data('fwhm_y')
        attr.set_value(self.attr_fwhm_y_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.fwhm_y_read
        
    def read_roi_sum(self, attr):
        self.debug_stream("In read_roi_sum()")
        #----- PROTECTED REGION ID(LMAnalysis.roi_sum_read) ENABLED START -----#
        self.attr_roi_sum_read = self.camera.get_data('sum')
        attr.set_value(self.attr_roi_sum_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.roi_sum_read
        
    def read_scan_parameter(self, attr):
        self.debug_stream("In read_scan_parameter()")
        #----- PROTECTED REGION ID(LMAnalysis.scan_parameter_read) ENABLED START -----#
        attr.set_value(self.attr_scan_parameter_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.scan_parameter_read
        
    def write_scan_parameter(self, attr):
        self.debug_stream("In write_scan_parameter()")
        data = attr.get_write_value()
        #----- PROTECTED REGION ID(LMAnalysis.scan_parameter_write) ENABLED START -----#
        self.attr_scan_parameter_read = data
        #----- PROTECTED REGION END -----#	//	LMAnalysis.scan_parameter_write
        
    def read_value(self, attr):
        self.debug_stream("In read_value()")
        #----- PROTECTED REGION ID(LMAnalysis.value_read) ENABLED START -----#
        try:
            self.attr_value_read = self.camera.get_data(self.attr_scan_parameter_read)
        except:
            self.attr_value_read = 0
        attr.set_value(self.attr_value_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.value_read
        
    def read_roi_x(self, attr):
        self.debug_stream("In read_roi_x()")
        #----- PROTECTED REGION ID(LMAnalysis.roi_x_read) ENABLED START -----#
        attr.set_value(self.attr_roi_x_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.roi_x_read
        
    def write_roi_x(self, attr):
        self.debug_stream("In write_roi_x()")
        data = attr.get_write_value()
        #----- PROTECTED REGION ID(LMAnalysis.roi_x_write) ENABLED START -----#
        self.attr_roi_x_read = data
        self.camera.set_new_roi([self.attr_roi_x_read, self.attr_roi_y_read,
                                 self.attr_roi_h_read, self.attr_roi_w_read])
        #----- PROTECTED REGION END -----#	//	LMAnalysis.roi_x_write
        
    def read_roi_y(self, attr):
        self.debug_stream("In read_roi_y()")
        #----- PROTECTED REGION ID(LMAnalysis.roi_y_read) ENABLED START -----#
        attr.set_value(self.attr_roi_y_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.roi_y_read
        
    def write_roi_y(self, attr):
        self.debug_stream("In write_roi_y()")
        data = attr.get_write_value()
        #----- PROTECTED REGION ID(LMAnalysis.roi_y_write) ENABLED START -----#
        self.attr_roi_y_read = data
        self.camera.set_new_roi([self.attr_roi_x_read, self.attr_roi_y_read,
                                 self.attr_roi_h_read, self.attr_roi_w_read])
        #----- PROTECTED REGION END -----#	//	LMAnalysis.roi_y_write
        
    def read_roi_w(self, attr):
        self.debug_stream("In read_roi_w()")
        #----- PROTECTED REGION ID(LMAnalysis.roi_w_read) ENABLED START -----#
        attr.set_value(self.attr_roi_w_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.roi_w_read
        
    def write_roi_w(self, attr):
        self.debug_stream("In write_roi_w()")
        data = attr.get_write_value()
        #----- PROTECTED REGION ID(LMAnalysis.roi_w_write) ENABLED START -----#
        self.attr_roi_w_read = data
        self.camera.set_new_roi([self.attr_roi_x_read, self.attr_roi_y_read,
                                 self.attr_roi_h_read, self.attr_roi_w_read])
        #----- PROTECTED REGION END -----#	//	LMAnalysis.roi_w_write
        
    def read_roi_h(self, attr):
        self.debug_stream("In read_roi_h()")
        #----- PROTECTED REGION ID(LMAnalysis.roi_h_read) ENABLED START -----#
        attr.set_value(self.attr_roi_h_read)
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.roi_h_read
        
    def write_roi_h(self, attr):
        self.debug_stream("In write_roi_h()")
        data = attr.get_write_value()
        #----- PROTECTED REGION ID(LMAnalysis.roi_h_write) ENABLED START -----#
        self.attr_roi_h_read = data
        self.camera.set_new_roi([self.attr_roi_x_read, self.attr_roi_y_read,
                                 self.attr_roi_h_read, self.attr_roi_w_read])
        #----- PROTECTED REGION END -----#	//	LMAnalysis.roi_h_write
        
    
    
            
    def read_attr_hardware(self, data):
        self.debug_stream("In read_attr_hardware()")
        #----- PROTECTED REGION ID(LMAnalysis.read_attr_hardware) ENABLED START -----#
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.read_attr_hardware


    # -------------------------------------------------------------------------
    #    LMAnalysis command methods
    # -------------------------------------------------------------------------
    
    def Start(self):
        """ does analysis of last frame
        """
        self.debug_stream("In Start()")
        #----- PROTECTED REGION ID(LMAnalysis.Start) ENABLED START -----#
        if self.get_state != DevState.FAULT:
            self._refresh_thread_state = 'runnig'
            self._refresh_thread.start()
            self.set_state(DevState.RUNNING)
        #----- PROTECTED REGION END -----#	//	LMAnalysis.Start
        
    def Stop(self):
        """ 
        """
        self.debug_stream("In Stop()")
        #----- PROTECTED REGION ID(LMAnalysis.Stop) ENABLED START -----#
        self._refresh_thread_state = 'stopped'
        self.set_state(DevState.ON)
        #----- PROTECTED REGION END -----#	//	LMAnalysis.Stop
        

    #----- PROTECTED REGION ID(LMAnalysis.programmer_methods) ENABLED START -----#

    def _refresh_data(self):
        while self._refresh_thread_state != 'stopped':
            time.sleep(POLL_PERIOD / 1000)
            self.attr_max_x_read = self.camera.get_data('max_x')
            self.attr_max_y_read = self.camera.get_data('max_y')
            self.attr_max_intensity_read = self.camera.get_data('max_i')
            self.attr_com_x_read = self.camera.get_data('com_x')
            self.attr_com_y_read = self.camera.get_data('com_y')
            self.attr_fwhm_x_read = self.camera.get_data('fwhm_x')
            self.attr_fwhm_y_read = self.camera.get_data('fwhm_y')
            self.attr_roi_sum_read = self.camera.get_data('sum')

    #----- PROTECTED REGION END -----#	//	LMAnalysis.programmer_methods

class LMAnalysisClass(PyTango.DeviceClass):
    # -------- Add you global class variables here --------------------------
    #----- PROTECTED REGION ID(LMAnalysis.global_class_variables) ENABLED START -----#
    
    #----- PROTECTED REGION END -----#	//	LMAnalysis.global_class_variables


    #    Class Properties
    class_property_list = {
        }


    #    Device Properties
    device_property_list = {
        'CameraDevice':
            [PyTango.DevString, 
            "Adress of related camera tango server",
            [] ],
        }


    #    Command definitions
    cmd_list = {
        'Start':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        'Stop':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        }


    #    Attribute definitions
    attr_list = {
        'max_x':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'unit': "px",
                'display unit': "px",
                'description': "x coordinate of intensity maxumum within ROI",
            } ],
        'max_y':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'unit': "px",
                'display unit': "px",
                'description': "y coordinate of intensity maxumum within ROI",
            } ],
        'max_intensity':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'description': "maxumum intensity value in ROI",
            } ],
        'com_x':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'description': "x coordinate of ROI's center of mass",
            } ],
        'com_y':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'description': "y coordinate of ROI's center of mass",
            } ],
        'fwhm_x':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'unit': "px",
                'display unit': "px",
                'description': "horizontal size of peak wihtin ROI",
            } ],
        'fwhm_y':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'unit': "px",
                'display unit': "px",
                'description': "vertical size of peak wihtin ROI",
            } ],
        'roi_sum':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'description': "sum of intensity over ROI",
            } ],
        'scan_parameter':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'description': "which parameter will be use as a ``source`` for Sardana. Can be `max_i`, `max_x`, `max_y`, `com_x`, `com_y`, `fwhm_x`, `fwhm_y`, `sum`",
                'Memorized':"true"
            } ],
        'value':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'description': "value to be passed to Sardana",
            } ],
        'roi_x':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'unit': "px",
                'display unit': "px",
                'description': "x coordinate of left top ROI corner",
                'Memorized':"true"
            } ],
        'roi_y':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'unit': "px",
                'display unit': "px",
                'description': "y coordinate of left top ROI corner",
            } ],
        'roi_w':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'unit': "px",
                'display unit': "px",
                'description': "ROI width",
            } ],
        'roi_h':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'unit': "px",
                'display unit': "px",
                'description': "ROI height",
            } ],
        }


def main():
    try:
        py = PyTango.Util(sys.argv)
        py.add_class(LMAnalysisClass, LMAnalysis, 'LMAnalysis')
        #----- PROTECTED REGION ID(LMAnalysis.add_classes) ENABLED START -----#
        
        #----- PROTECTED REGION END -----#	//	LMAnalysis.add_classes

        U = PyTango.Util.instance()
        U.server_init()
        U.server_run()

    except PyTango.DevFailed as e:
        print ('-------> Received a DevFailed exception:', e)
    except Exception as e:
        print ('-------> An unforeseen exception occured....', e)

if __name__ == '__main__':
    main()
