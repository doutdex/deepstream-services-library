
DSL_RESULT_COMPONENT_RESULT                 =  0x00010000
DSL_RESULT_COMPONENT_NAME_NOT_UNIQUE        =  0x00010001
DSL_RESULT_COMPONENT_NAME_NOT_FOUND         =  0x00010010
DSL_RESULT_COMPONENT_NAME_BAD_FORMAT        =  0x00010011
DSL_RESULT_COMPONENT_IN_USE                 =  0x00010100
DSL_RESULT_COMPONENT_NOT_USED_BY_PIPELINE   =  0x00010101

# Source API Return Values

DSL_RESULT_SOURCE_RESULT                    =  0x00100000
DSL_RESULT_SOURCE_NAME_NOT_UNIQUE           =  0x00100001
DSL_RESULT_SOURCE_NAME_NOT_FOUND            =  0x00100010
DSL_RESULT_SOURCE_NAME_BAD_FORMAT           =  0x00100011
DSL_RESULT_SOURCE_NEW_EXCEPTION             =  0x00100100
DSL_RESULT_SOURCE_STREAM_FILE_NOT_FOUND     =  0x00100101

#  Sink Oxject Return Values

DSL_RESULT_SINK_RESULT                      =  0x01000000
DSL_RESULT_SINK_NAME_NOT_UNIQUE             =  0x01000001
DSL_RESULT_SINK_NAME_NOT_FOUND              =  0x01000010
DSL_RESULT_SINK_NAME_BAD_FORMAT             =  0x01000011
DSL_RESULT_SINK_NEW_EXCEPTION               =  0x01000100

#  OSD Oxject Return Values

DSL_RESULT_OSD_RESULT                       =  0x01010000
DSL_RESULT_OSD_NAME_NOT_UNIQUE              =  0x01010001
DSL_RESULT_OSD_NAME_NOT_FOUND               =  0x01010010
DSL_RESULT_OSD_NAME_BAD_FORMAT              =  0x01010011
DSL_RESULT_OSD_NEW_EXCEPTION                =  0x01010100


#  GIE Oxject Return Values
 
DSL_RESULT_GIE_RESULT                       =  0x01100000
DSL_RESULT_GIE_NAME_NOT_UNIQUE              =  0x01100001
DSL_RESULT_GIE_NAME_NOT_FOUND               =  0x01100010
DSL_RESULT_GIE_NAME_BAD_FORMAT              =  0x01100011
DSL_RESULT_GIE_CONFIG_FILE_NOT_FOUND        =  0x01100100
DSL_RESULT_GIE_MODEL_FILE_NOT_FOUND         =  0x01100100
DSL_RESULT_GIE_NEW_EXCEPTION                =  0x01100100

DSL_RESULT_DISPLAY_RESULT                   =  0x10000000
DSL_RESULT_DISPLAY_NAME_NOT_UNIQUE          =  0x10000001
DSL_RESULT_DISPLAY_NAME_NOT_FOUND           =  0x10000010
DSL_RESULT_DISPLAY_NAME_BAD_FORMAT          =  0x10000011
DSL_RESULT_DISPLAY_NEW_EXCEPTION            =  0x10000100


#  Pipeline Oxject Return Values

DSL_RESULT_PIPELINE_RESULT                  =   0x11000000
DSL_RESULT_PIPELINE_NAME_NOT_UNIQUE         =   0x11000001
DSL_RESULT_PIPELINE_NAME_NOT_FOUND          =   0x11000010
DSL_RESULT_PIPELINE_NAME_BAD_FORMAT         =   0x11000011
DSL_RESULT_PIPELINE_STATE_PAUSED            =   0x11000100
DSL_RESULT_PIPELINE_STATE_RUNNING           =   0x11000101
DSL_RESULT_PIPELINE_NEW_EXCEPTION           =   0x11000110
DSL_RESULT_PIPELINE_COMPONENT_ADD_FAILED    =   0x11000111
DSL_RESULT_PIPELINE_COMPONENT_REMOVE_FAILED =   0x11001000
DSL_RESULT_PIPELINE_STREAMMUX_SETUP_FAILED  =   0x11001001
DSL_RESULT_PIPELINE_FAILED_TO_PLAY          =   0x11001010
DSL_RESULT_PIPELINE_FAILED_TO_PAUSE         =   0x11001011
DSL_RESULT_PIPELINE_LISTENER_NOT_UNIQUE     =   0x11001100
DSL_RESULT_PIPELINE_LISTENER_NOT_FOUND      =   0x11001101
DSL_RESULT_PIPELINE_HANDLER_NOT_UNIQUE      =   0x11001110
DSL_RESULT_PIPELINE_HANDLER_NOT_FOUND       =   0x11001111
DSL_RESULT_PIPELINE_SUBSCRIBER_NOT_UNIQUE   =   0x11010001
DSL_RESULT_PIPELINE_SUBSCRIBER_NOT_FOUND    =   0x11010010

DSL_CUDADEC_MEMTYPE_DEVICE                  =   0
DSL_CUDADEC_MEMTYPE_PINNED                  =   1
DSL_CUDADEC_MEMTYPE_UNIFIED                 =   2

DSL_PIPELINE_STATE_NULL                     =   0
DSL_PIPELINE_STATE_READY                    =   1
DSL_PIPELINE_STATE_PLAYING                  =   2
