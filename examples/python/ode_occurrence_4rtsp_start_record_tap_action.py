<<<<<<< HEAD:examples/python/ode_occurrence_rtsp_start_record_tap_action.py
################################################################################	
# The MIT License	
#	
# Copyright (c) 2019-2020, Robert Howell. All rights reserved.	
#	
# Permission is hereby granted, free of charge, to any person obtaining a	
# copy of this software and associated documentation files (the "Software"),	
# to deal in the Software without restriction, including without limitation	
# the rights to use, copy, modify, merge, publish, distribute, sublicense,	
# and/or sell copies of the Software, and to permit persons to whom the	
# Software is furnished to do so, subject to the following conditions:	
#	
# The above copyright notice and this permission notice shall be included in	
# all copies or substantial portions of the Software.	
#	
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR	
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,	
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL	
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER	
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING	
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER	
# DEALINGS IN THE SOFTWARE.	
################################################################################	

#!/usr/bin/env python	

import sys	
sys.path.insert(0, "../../")	
import time	
from dsl import *	

# RTSP Source URI	
src_url_0 = 'rtsp://user:password@192.168.0.14:554/Streaming/Channels/101'	

# Filespecs for the Primary GIE	
primary_infer_config_file = '../../test/configs/config_infer_primary_nano.txt'	
primary_model_engine_file = '../../test/models/Primary_Detector_Nano/resnet10.caffemodel_b8_gpu0_fp16.engine'	
tracker_config_file = '../../test/configs/iou_config.txt'	

TILER_WIDTH = DSL_DEFAULT_STREAMMUX_WIDTH	
TILER_HEIGHT = DSL_DEFAULT_STREAMMUX_HEIGHT	
WINDOW_WIDTH = DSL_DEFAULT_STREAMMUX_WIDTH	
WINDOW_HEIGHT = DSL_DEFAULT_STREAMMUX_HEIGHT	

PGIE_CLASS_ID_VEHICLE = 0	
PGIE_CLASS_ID_BICYCLE = 1	
PGIE_CLASS_ID_PERSON = 2	
PGIE_CLASS_ID_ROADSIGN = 3	

## 	
# Function to be called on XWindow KeyRelease event	
## 	
def xwindow_key_event_handler(key_string, client_data):	
    print('key released = ', key_string)	
    if key_string.upper() == 'P':	
        dsl_pipeline_pause('pipeline')	
    elif key_string.upper() == 'R':	
        dsl_pipeline_play('pipeline')	
    elif key_string.upper() == 'Q' or key_string == '' or key_string == '':	
        dsl_main_loop_quit()	

## 	
# Function to be called on XWindow Delete event	
## 	
def xwindow_delete_event_handler(client_data):	
    print('delete window event')	
    dsl_main_loop_quit()	

## 	
# Function to be called on End-of-Stream (EOS) event	
## 	
def eos_event_listener(client_data):	
    print('Pipeline EOS event')	
    dsl_main_loop_quit()	

## 	
# Function to be called on every change of Pipeline state	
## 	
def state_change_listener(old_state, new_state, client_data):	
    print('previous state = ', old_state, ', new state = ', new_state)	
    if new_state == DSL_STATE_PLAYING:	
        dsl_pipeline_dump_to_dot('pipeline', "state-playing")	

## 	
# Function to create all Display Types used in this example	
## 	
def create_display_types():	

    # ````````````````````````````````````````````````````````````````````````````````````````````````````````	
    # Create new RGBA color types	
    retval = dsl_display_type_rgba_color_new('full-red', red=1.0, blue=0.0, green=0.0, alpha=1.0)	
    if retval != DSL_RETURN_SUCCESS:	
        return retval	
    retval = dsl_display_type_rgba_color_new('full-white', red=1.0, blue=1.0, green=1.0, alpha=1.0)	
    if retval != DSL_RETURN_SUCCESS:	
        return retval	
    retval = dsl_display_type_rgba_color_new('opaque-black', red=0.0, blue=0.0, green=0.0, alpha=0.8)	
    if retval != DSL_RETURN_SUCCESS:	
        return retval	
    retval = dsl_display_type_rgba_font_new('impact-20-white', font='impact', size=20, color='full-white')	
    if retval != DSL_RETURN_SUCCESS:	
        return retval	

    # Create a new Text type object that will be used to show the recording in progress	
    retval = dsl_display_type_rgba_text_new('rec-text', 'REC    ', x_offset=10, y_offset=30, 	
        font='impact-20-white', has_bg_color=True, bg_color='opaque-black')	
    if retval != DSL_RETURN_SUCCESS:	
        return retval	
    # A new RGBA Circle to be used to simulate a red LED light for the recording in progress.	
    return dsl_display_type_rgba_circle_new('red-led', x_center=94, y_center=52, radius=8, 	
        color='full-red', has_bg_color=True, bg_color='full-red')	


## 	
# Objects of this class will be used as "client_data" for all callback notifications.	
# defines a class of all component names associated with a single RTSP Source. 	
# The names are derived from the unique Source name	
##	
class ComponentNames:	
    def __init__(self, source):	
        self.source = source	
        self.occurrence_trigger = source + '-occurrence-trigger'	
        self.record_tap = source + '-record-tap'	
        self.ode_notify = source + '-ode-notify'	
        self.start_record = source + '-start-record'    	

def RecordingStarted(event_id, trigger,	
    buffer, frame_meta, object_meta, client_data):	

    # cast the C void* client_data back to a py_object pointer and deref	
    components = cast(client_data, POINTER(py_object)).contents.value	

    # a good place to enabled an Always Trigger that adds `REC` text to the frame which can	
    # be disabled in the RecordComplete callback below. And/or send notifictions to external clients.	

    # in this example we will call on the Tiler to show the source that started recording.	
    dsl_tiler_source_show_set('tiler', source=components.source, timeout=duration, has_precedence=True)	

##	
# Callback function to process all "record-complete" notifications	
##	
def RecordComplete(session_info, client_data):	

    # session_info is obtained using the NVIDIA python bindings	

    # cast the C void* client_data back to a py_object pointer and deref	
    components = cast(client_data, POINTER(py_object)).contents.value	

    # reset the Trigger that started this recording so that a new session can be started.	
    dsl_ode_trigger_reset(components.occurrence_trigger)	

##	
# Function to create all "1-per-source" components, and add them to the Pipeline	
# pipeline - unique name of the Pipeline to add the Source components to	
# source - unique name for the RTSP Source to create	
# uri - unique uri for the new RTSP Source	
# ode_handler - Object Detection Event (ODE) handler to add the new Trigger and Actions to	
##	
def CreatePerSourceComponents(pipeline, source, rtsp_uri, ode_handler):	

    # New Component names based on unique source name	
    components = ComponentNames(source)	

    # For each camera, create a new RTSP Source for the specific RTSP URI	
    retval = dsl_source_rtsp_new(source, 	
        uri = rtsp_uri, 	
        protocol = DSL_RTP_ALL, 	
        cudadec_mem_type = DSL_CUDADEC_MEMTYPE_DEVICE, 	
        intra_decode = False, 	
        drop_frame_interval = 0, 	
        latency=100)	
    if (retval != DSL_RETURN_SUCCESS):	
        return retval	

    # New record tap created with our common RecordComplete callback function defined above	
    retval = dsl_tap_record_new(components.record_tap, 	
        outdir = './recordings/', 	
        container = DSL_CONTAINER_MKV, 	
        client_listener = RecordComplete)	
    if (retval != DSL_RETURN_SUCCESS):	
        return retval	

    # Add the new Tap to the Source directly	
    retval = dsl_source_rtsp_tap_add(source, tap=components.record_tap)	
    if (retval != DSL_RETURN_SUCCESS):	
        return retval	

    # Next, create the Person Occurrence Trigger. We will reset the trigger in the recording complete callback	
    retval = dsl_ode_trigger_occurrence_new(components.occurrence_trigger, 	
        source=source, class_id=PGIE_CLASS_ID_PERSON, limit=1)	
    if (retval != DSL_RETURN_SUCCESS):	
        return retval	

    # New (optional) Custom Action to be notified of ODE Occurrence, and pass component names as client data.	
    retval = dsl_ode_action_custom_new(components.ode_notify, 	
        client_handler=RecordingStarted, client_data=components)	
    if (retval != DSL_RETURN_SUCCESS):	
        return retval	

    # Create a new Action to start the record session for this Source, with the component names as client data	
    retval = dsl_ode_action_tap_record_start_new(components.start_record, 	
        record_tap=components.record_tap, start=15, duration=360, client_data=components)	
    if (retval != DSL_RETURN_SUCCESS):	
        return retval	

    # Add the Actions to the trigger for this source. 	
    retval = dsl_ode_trigger_action_add_many(components.occurrence_trigger, 	
        actions=[components.ode_notify, components.start_record, None])	
    if (retval != DSL_RETURN_SUCCESS):	
        return retval	

    # Add the new Source with its Record-Tap to the Pipeline	
    retval = dsl_pipeline_component_add(pipeline, source)	
    if (retval != DSL_RETURN_SUCCESS):	
        return retval	

    # Add the new Trigger to the ODE Pad Probe Handler	
    return dsl_pph_ode_trigger_add(ode_handler, components.occurrence_trigger)	


def main(args):	

    # Since we're not using args, we can Let DSL initialize GST on first call	
    while True:	

        # ````````````````````````````````````````````````````````````````````````````````````````````````````````	
        # This example is used to demonstrate the use of First Occurrence Triggers and Start Record Actions	
        # to control Record Taps with a multi camera setup	

        retval = create_display_types()    	
        if retval != DSL_RETURN_SUCCESS:	
            break	

        # Create a new Action to display the "recording in-progress" text	
        retval = dsl_ode_action_display_meta_add_new('rec-text-overlay', 'rec-text')	
        if retval != DSL_RETURN_SUCCESS:	
            break	
        # Create a new Action to display the "recording in-progress" LED	
        retval = dsl_ode_action_display_meta_add_new('red-led-overlay', 'red-led')	
        if retval != DSL_RETURN_SUCCESS:	
            break	

        # New Primary GIE using the filespecs above, with interval and Id	
        retval = dsl_gie_primary_new('primary-gie', primary_infer_config_file, primary_model_engine_file, 2)	
        if retval != DSL_RETURN_SUCCESS:	
            break	

        # New KTL Tracker, setting max width and height of input frame	
        retval = dsl_tracker_iou_new('iou-tracker', tracker_config_file, 480, 272)	
        if retval != DSL_RETURN_SUCCESS:	
            break	

        # New Tiled Display, setting width and height, use default cols/rows set by source count	
        retval = dsl_tiler_new('tiler', TILER_WIDTH, TILER_HEIGHT)	
        if retval != DSL_RETURN_SUCCESS:	
            break	

        # Object Detection Event (ODE) Pad Probe Handler (PPH) to manage our ODE Triggers with their ODE Actions	
        retval = dsl_pph_ode_new('ode-handler')	
        if (retval != DSL_RETURN_SUCCESS):	
            break	

        # Add the ODE Pad Probe Hanlder to the Sink Pad of the Tiler	
        retval = dsl_tiler_pph_add('tiler', 'ode-handler', DSL_PAD_SINK)	
        if retval != DSL_RETURN_SUCCESS:	
            break	

        # New OSD with clock enabled... using default values.	
        retval = dsl_osd_new('on-screen-display', True)	
        if retval != DSL_RETURN_SUCCESS:	
            break	

        # New Overlay Sink, 0 x/y offsets and same dimensions as Tiled Display	
        retval = dsl_sink_window_new('window-sink', 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)	
        if retval != DSL_RETURN_SUCCESS:	
            break	

        # Add all the components to our pipeline	
        retval = dsl_pipeline_new_component_add_many('pipeline', 	
            ['primary-gie', 'iou-tracker', 'tiler', 'on-screen-display', 'window-sink', None])	
        if retval != DSL_RETURN_SUCCESS:	
            break	

       # For each of our four sources, call the funtion to create the source-specific components.	
        retval = CreatePerSourceComponents('pipeline', 'src-0', src_url_0, 'ode-handler')	
        if (retval != DSL_RETURN_SUCCESS):	
            break	

        # Add the XWindow event handler functions defined above	
        retval = dsl_pipeline_xwindow_key_event_handler_add("pipeline", xwindow_key_event_handler, None)	
        if retval != DSL_RETURN_SUCCESS:	
            break	
        retval = dsl_pipeline_xwindow_delete_event_handler_add("pipeline", xwindow_delete_event_handler, None)	
        if retval != DSL_RETURN_SUCCESS:	
            break	

        ## Add the listener callback functions defined above	
        retval = dsl_pipeline_state_change_listener_add('pipeline', state_change_listener, None)	
        if retval != DSL_RETURN_SUCCESS:	
            break	
        retval = dsl_pipeline_eos_listener_add('pipeline', eos_event_listener, None)	
        if retval != DSL_RETURN_SUCCESS:	
            break	

        # Play the pipeline	
        retval = dsl_pipeline_play('pipeline')	
        if retval != DSL_RETURN_SUCCESS:	
            break	

        dsl_main_loop_run()	
        retval = DSL_RETURN_SUCCESS	
        break	

        # Print out the final result	
        print(dsl_return_value_to_string(retval))	

    dsl_delete_all()	

if __name__ == '__main__':	
=======
################################################################################
# The MIT License
#
# Copyright (c) 2019-2020, Robert Howell. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
################################################################################

#!/usr/bin/env python

import sys
sys.path.insert(0, "../../")
import time
from dsl import *

# RTSP Source URI
src_url_0 = 'rtsp://username:password@192.168.1.64:554/Streaming/Channels/101'
src_url_1 = 'rtsp://username:password@192.168.1.65:554/Streaming/Channels/101'
src_url_2 = 'rtsp://username:password@192.168.1.66:554/Streaming/Channels/101'
src_url_3 = 'rtsp://username:password@192.168.1.67:554/Streaming/Channels/101'

# Filespecs for the Primary GIE
primary_infer_config_file = '../../test/configs/config_infer_primary_nano.txt'
primary_model_engine_file = '../../test/models/Primary_Detector_Nano/resnet10.caffemodel_b8_gpu0_fp16.engine'
tracker_config_file = '../../test/configs/iou_config.txt'

TILER_WIDTH = DSL_DEFAULT_STREAMMUX_WIDTH
TILER_HEIGHT = DSL_DEFAULT_STREAMMUX_HEIGHT
WINDOW_WIDTH = DSL_DEFAULT_STREAMMUX_WIDTH
WINDOW_HEIGHT = DSL_DEFAULT_STREAMMUX_HEIGHT

PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3

## 
# Function to be called on XWindow KeyRelease event
## 
def xwindow_key_event_handler(key_string, client_data):
    print('key released = ', key_string)
    if key_string.upper() == 'P':
        dsl_pipeline_pause('pipeline')
    elif key_string.upper() == 'R':
        dsl_pipeline_play('pipeline')
    elif key_string.upper() == 'Q' or key_string == '' or key_string == '':
        dsl_main_loop_quit()
 
## 
# Function to be called on XWindow Delete event
## 
def xwindow_delete_event_handler(client_data):
    print('delete window event')
    dsl_main_loop_quit()

## 
# Function to be called on End-of-Stream (EOS) event
## 
def eos_event_listener(client_data):
    print('Pipeline EOS event')
    dsl_main_loop_quit()

## 
# Function to be called on New-Error-Message received by the Pipeline bus-watcher
## 
def error_message_handler(source, message, client_data):
    print('Error: source =', source, 'message =', message)

## 
# Function to be called on every Pipeline change of state
## 
def pipeline_state_change_listener(old_state, new_state, client_data):

    print('Pipeline change-of-state: previous = ', dsl_state_value_to_string(old_state),
        ', new = ', dsl_state_value_to_string(new_state))

    if new_state == DSL_STATE_PLAYING:
        dsl_pipeline_dump_to_dot('pipeline', "state-playing")

##
# Function to be called on every RTSP Source change of state
##
def source_state_change_listener(old_state, new_state, client_data):

    # cast the C void* client_data back to a py_object pointer and deref
    components = cast(client_data, POINTER(py_object)).contents.value

    print('RTSP Source ', components.source, 'change-of-state: previous =',
        dsl_state_value_to_string(old_state), '- new =', dsl_state_value_to_string(new_state))
    
    if (new_state == DSL_STATE_NULL or new_state == DSL_STATE_PLAYING):
        retval, data = dsl_source_rtsp_connection_data_get(components.source)
        print('Connection data for source:', components.source)
        print('  is connected:     ', data.is_connected)
        print('  first connected:  ', time.ctime(data.first_connected))
        print('  last connected:   ', time.ctime(data.last_connected))
        print('  last disconnected:', time.ctime(data.last_disconnected))
        print('  total count:      ', data.count)
        print('  in-reconnect:     ', data.is_in_reconnect)
        print('  retries:          ', data.retries)
        print('  sleep time:       ', data.sleep,'seconds')
        print('  timeout:          ', data.timeout, 'seconds')

        if (new_state == DSL_STATE_PLAYING):
            print("setting the time to sleep between re-connection retries to 4 seconds for quick recovery")
            dsl_source_rtsp_reconnection_params_set(components.source, sleep=4, timeout=30)
            
        # If we're in a re-connection cycle, check if the nuber of quick recovery attempts has
        # been reached. (20 * 4 =~ 80 seconds), before backing off on the time between retries 
        elif (data.is_in_reconnect and data.retries == 20):
            print("extending the time to sleep between re-connection retries to 20 seconds")
            dsl_source_rtsp_reconnection_params_set(components.source, sleep=20, timeout=30)

## 
# Function to create all Display Types used in this example
## 
def create_display_types():

    # ````````````````````````````````````````````````````````````````````````````````````````````````````````
    # Create new RGBA color types
    retval = dsl_display_type_rgba_color_new('full-red', red=1.0, blue=0.0, green=0.0, alpha=1.0)
    if retval != DSL_RETURN_SUCCESS:
        return retval
    retval = dsl_display_type_rgba_color_new('full-white', red=1.0, blue=1.0, green=1.0, alpha=1.0)
    if retval != DSL_RETURN_SUCCESS:
        return retval
    retval = dsl_display_type_rgba_color_new('opaque-black', red=0.0, blue=0.0, green=0.0, alpha=0.8)
    if retval != DSL_RETURN_SUCCESS:
        return retval
    retval = dsl_display_type_rgba_font_new('impact-20-white', font='impact', size=20, color='full-white')
    if retval != DSL_RETURN_SUCCESS:
        return retval
        
    # Create a new Text type object that will be used to show the recording in progress
    retval = dsl_display_type_rgba_text_new('rec-text', 'REC    ', x_offset=10, y_offset=30, 
        font='impact-20-white', has_bg_color=True, bg_color='opaque-black')
    if retval != DSL_RETURN_SUCCESS:
        return retval
    # A new RGBA Circle to be used to simulate a red LED light for the recording in progress.
    return dsl_display_type_rgba_circle_new('red-led', x_center=94, y_center=52, radius=8, 
        color='full-red', has_bg_color=True, bg_color='full-red')

## 
# Objects of this class will be used as "client_data" for all callback notifications.
# defines a class of all component names associated with a single RTSP Source. 
# The names are derived from the unique Source name
##
class ComponentNames:
    def __init__(self, source):
        self.source = source
        self.occurrence_trigger = source + '-occurrence-trigger'
        self.record_tap = source + '-record-tap'
        self.ode_notify = source + '-ode-notify'
        self.start_record = source + '-start-record'    

def recording_started(event_id, trigger,
    buffer, frame_meta, object_meta, client_data):

    # cast the C void* client_data back to a py_object pointer and deref
    components = cast(client_data, POINTER(py_object)).contents.value
    
## 
# Function to be called on recording complete
## 
def record_complete_listener(session_info_ptr, client_data):
    print(' ***  Recording Complete  *** ')

    # cast the C void* client_data back to a py_object pointer and deref
    components = cast(client_data, POINTER(py_object)).contents.value
    
    session_info = session_info_ptr.contents
    print('session Id:     ', session_info.session_id)
    print('filename:       ', session_info.filename)
    print('dirpath:        ', session_info.dirpath)
    print('duration:       ', session_info.duration)
    print('container type: ', session_info.container_type)
    print('width:          ', session_info.width)
    print('height:         ', session_info.height)
    
    retval, is_on = dsl_tap_record_is_on_get(components.record_tap)
    print('is_on flag = ', is_on)
    
    retval, reset_done = dsl_tap_record_reset_done_get(components.record_tap)
    print('reset_done flag = ', reset_done)
    
    # reset the Trigger that started this recording so that a new session can be started.
    dsl_ode_trigger_reset(components.occurrence_trigger)
    
    return None    

    
##
# Function to create all "1-per-source" components, and add them to the Pipeline
# pipeline - unique name of the Pipeline to add the Source components to
# source - unique name for the RTSP Source to create
# uri - unique uri for the new RTSP Source
# ode_handler - Object Detection Event (ODE) handler to add the new Trigger and Actions to
##
def CreatePerSourceComponents(pipeline, source, rtsp_uri, ode_handler):
   
    # New Component names based on unique source name
    components = ComponentNames(source)
    
    # For each camera, create a new RTSP Source for the specific RTSP URI
    retval = dsl_source_rtsp_new(source, 
        uri = rtsp_uri, 
        protocol = DSL_RTP_ALL, 
        cudadec_mem_type = DSL_CUDADEC_MEMTYPE_DEVICE, 
        intra_decode = False, 
        drop_frame_interval = 0, 
        latency=100,
        timeout=3)
    if (retval != DSL_RETURN_SUCCESS):
        return retval
        
    # Add our state change listener to the new source, with the component names as client data
    retval = dsl_source_rtsp_state_change_listener_add(source, 
        client_listener=source_state_change_listener,
        client_data=components)
    if (retval != DSL_RETURN_SUCCESS):
        return retval

    # New record tap created with our common record_complete_listener callback function defined above
    retval = dsl_tap_record_new(components.record_tap, 
        outdir = './recordings/', 
        container = DSL_CONTAINER_MKV, 
        client_listener = record_complete_listener)
    if (retval != DSL_RETURN_SUCCESS):
        return retval

    # Add the new Tap to the Source directly
    retval = dsl_source_rtsp_tap_add(source, tap=components.record_tap)
    if (retval != DSL_RETURN_SUCCESS):
        return retval

    # Next, create the Person Occurrence Trigger. We will reset the trigger in the recording complete callback
    retval = dsl_ode_trigger_occurrence_new(components.occurrence_trigger, 
        source=source, class_id=PGIE_CLASS_ID_PERSON, limit=1)
    if (retval != DSL_RETURN_SUCCESS):
        return retval

    # New (optional) Custom Action to be notified of ODE Occurrence, and pass component names as client data.
    retval = dsl_ode_action_custom_new(components.ode_notify, 
        client_handler=recording_started, client_data=components)
    if (retval != DSL_RETURN_SUCCESS):
        return retval

    # Create a new Action to start the record session for this Source, with the component names as client data
    retval = dsl_ode_action_tap_record_start_new(components.start_record, 
        record_tap=components.record_tap, start=1, duration=15, client_data=components)
    if (retval != DSL_RETURN_SUCCESS):
        return retval
    
    # Add the Actions to the trigger for this source. 
    retval = dsl_ode_trigger_action_add_many(components.occurrence_trigger, 
        actions=[components.ode_notify, components.start_record, None])
    if (retval != DSL_RETURN_SUCCESS):
        return retval
    
    # Add the new Source with its Record-Tap to the Pipeline
    retval = dsl_pipeline_component_add(pipeline, source)
    if (retval != DSL_RETURN_SUCCESS):
        return retval
        
    # Add the new Trigger to the ODE Pad Probe Handler
    return dsl_pph_ode_trigger_add(ode_handler, components.occurrence_trigger)
    
    
def main(args):

    # Since we're not using args, we can Let DSL initialize GST on first call
    while True:

        # ````````````````````````````````````````````````````````````````````````````````````````````````````````
        # This example is used to demonstrate the use of First Occurrence Triggers and Start Record Actions
        # to control Record Taps with a multi camera setup

        retval = create_display_types()    
        if retval != DSL_RETURN_SUCCESS:
            break
            
        # Create a new Action to display the "recording in-progress" text
        retval = dsl_ode_action_display_meta_add_new('rec-text-overlay', 'rec-text')
        if retval != DSL_RETURN_SUCCESS:
            break
        # Create a new Action to display the "recording in-progress" LED
        retval = dsl_ode_action_display_meta_add_new('red-led-overlay', 'red-led')
        if retval != DSL_RETURN_SUCCESS:
            break
        
        # New Primary GIE using the filespecs above, with interval and Id
        retval = dsl_gie_primary_new('primary-gie', primary_infer_config_file, primary_model_engine_file, 2)
        if retval != DSL_RETURN_SUCCESS:
            break

        # New KTL Tracker, setting max width and height of input frame
        retval = dsl_tracker_iou_new('iou-tracker', tracker_config_file, 480, 272)
        if retval != DSL_RETURN_SUCCESS:
            break

        # New Tiled Display, setting width and height, use default cols/rows set by source count
        retval = dsl_tiler_new('tiler', TILER_WIDTH, TILER_HEIGHT)
        if retval != DSL_RETURN_SUCCESS:
            break

        # Object Detection Event (ODE) Pad Probe Handler (PPH) to manage our ODE Triggers with their ODE Actions
        retval = dsl_pph_ode_new('ode-handler')
        if (retval != DSL_RETURN_SUCCESS):
            break
            
        # Add the ODE Pad Probe Hanlder to the Sink Pad of the Tiler
        retval = dsl_tiler_pph_add('tiler', 'ode-handler', DSL_PAD_SINK)
        if retval != DSL_RETURN_SUCCESS:
            break

        # New OSD with clock enabled... using default values.
        retval = dsl_osd_new('on-screen-display', True)
        if retval != DSL_RETURN_SUCCESS:
            break

        # New Overlay Sink, 0 x/y offsets and same dimensions as Tiled Display
        retval = dsl_sink_window_new('window-sink', 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        if retval != DSL_RETURN_SUCCESS:
            break

        # Add all the components to our pipeline
        retval = dsl_pipeline_new_component_add_many('pipeline', 
            ['primary-gie', 'iou-tracker', 'tiler', 'on-screen-display', 'window-sink', None])
        if retval != DSL_RETURN_SUCCESS:
            break

       # For each of our four sources, call the funtion to create the source-specific components.
        retval = CreatePerSourceComponents('pipeline', 'src-0', src_url_0, 'ode-handler')
        if (retval != DSL_RETURN_SUCCESS):
            break
        
        retval = CreatePerSourceComponents('pipeline', 'src-1', src_url_1, 'ode-handler')
        if (retval != DSL_RETURN_SUCCESS):
            break
        
        retval = CreatePerSourceComponents('pipeline', 'src-2', src_url_2, 'ode-handler')
        if (retval != DSL_RETURN_SUCCESS):
            break
        
        retval = CreatePerSourceComponents('pipeline', 'src-3', src_url_3, 'ode-handler')
        if (retval != DSL_RETURN_SUCCESS):
            break
        
        # Add the XWindow event handler functions defined above
        retval = dsl_pipeline_xwindow_key_event_handler_add("pipeline", xwindow_key_event_handler, None)
        if retval != DSL_RETURN_SUCCESS:
            break
        retval = dsl_pipeline_xwindow_delete_event_handler_add("pipeline", xwindow_delete_event_handler, None)
        if retval != DSL_RETURN_SUCCESS:
            break

        ## Add the listener callback functions defined above
        retval = dsl_pipeline_state_change_listener_add('pipeline', pipeline_state_change_listener, None)
        if retval != DSL_RETURN_SUCCESS:
            break
        retval = dsl_pipeline_eos_listener_add('pipeline', eos_event_listener, None)
        if retval != DSL_RETURN_SUCCESS:
            break
            
        retval = dsl_pipeline_error_message_handler_add('pipeline', error_message_handler, None)
        if retval != DSL_RETURN_SUCCESS:
            break

        # Play the pipeline
        retval = dsl_pipeline_play('pipeline')
        if retval != DSL_RETURN_SUCCESS:
            break

        dsl_main_loop_run()
        retval = DSL_RETURN_SUCCESS
        break

        # Print out the final result
        print(dsl_return_value_to_string(retval))

    dsl_delete_all()

if __name__ == '__main__':
>>>>>>> v0.08.alpha:examples/python/ode_occurrence_4rtsp_start_record_tap_action.py
    sys.exit(main(sys.argv))