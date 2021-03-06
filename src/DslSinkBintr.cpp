/*
The MIT License

Copyright (c) 2019-2021, Prominence AI, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in-
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

#include "Dsl.h"
#include "DslSinkBintr.h"
#include "DslBranchBintr.h"

namespace DSL
{

    SinkBintr::SinkBintr(const char* name, bool sync, bool async)
        : Bintr(name)
        , m_sync(sync)
        , m_async(async)
    {
        LOG_FUNC();

        m_pQueue = DSL_ELEMENT_NEW(NVDS_ELEM_QUEUE, "sink-bin-queue");
        AddChild(m_pQueue);
        m_pQueue->AddGhostPadToParent("sink");
    }

    SinkBintr::~SinkBintr()
    {
        LOG_FUNC();
    }

    bool SinkBintr::AddToParent(DSL_BASE_PTR pParentBintr)
    {
        LOG_FUNC();
        
        // add 'this' Sink to the Parent Pipeline 
        return std::dynamic_pointer_cast<BranchBintr>(pParentBintr)->
            AddSinkBintr(shared_from_this());
    }

    bool SinkBintr::IsParent(DSL_BASE_PTR pParentBintr)
    {
        LOG_FUNC();
        
        // check if 'this' Sink is child of Parent Pipeline 
        return std::dynamic_pointer_cast<BranchBintr>(pParentBintr)->
            IsSinkBintrChild(std::dynamic_pointer_cast<SinkBintr>(shared_from_this()));
    }

    bool SinkBintr::RemoveFromParent(DSL_BASE_PTR pParentBintr)
    {
        LOG_FUNC();
        
        if (!IsParent(pParentBintr))
        {
            LOG_ERROR("Sink '" << GetName() << "' is not a child of Pipeline '" << pParentBintr->GetName() << "'");
            return false;
        }
        // remove 'this' Sink from the Parent Pipeline 
        return std::dynamic_pointer_cast<BranchBintr>(pParentBintr)->
            RemoveSinkBintr(std::dynamic_pointer_cast<SinkBintr>(shared_from_this()));
    }

    void SinkBintr::GetSyncSettings(bool* sync, bool* async)
    {
        LOG_FUNC();
        
        *sync = m_sync;
        *async = m_async;
    }

    //-------------------------------------------------------------------------

    FakeSinkBintr::FakeSinkBintr(const char* name)
        : SinkBintr(name, true, false)
        , m_qos(false)
    {
        LOG_FUNC();
        
        m_pFakeSink = DSL_ELEMENT_NEW(NVDS_ELEM_SINK_FAKESINK, "sink-bin-fake");
        m_pFakeSink->SetAttribute("enable-last-sample", false);
        m_pFakeSink->SetAttribute("max-lateness", -1);
        m_pFakeSink->SetAttribute("sync", m_sync);
        m_pFakeSink->SetAttribute("async", m_async);
        m_pFakeSink->SetAttribute("qos", m_qos);
        
        AddChild(m_pFakeSink);
    }
    
    FakeSinkBintr::~FakeSinkBintr()
    {
        LOG_FUNC();
    
        if (IsLinked())
        {    
            UnlinkAll();
        }
    }

    bool FakeSinkBintr::LinkAll()
    {
        LOG_FUNC();
        
        if (m_isLinked)
        {
            LOG_ERROR("FakeSinkBintr '" << GetName() << "' is already linked");
            return false;
        }
        if (!m_pQueue->LinkToSink(m_pFakeSink))
        {
            return false;
        }
        m_isLinked = true;
        return true;
    }
    
    void FakeSinkBintr::UnlinkAll()
    {
        LOG_FUNC();
        
        if (!m_isLinked)
        {
            LOG_ERROR("FakeSinkBintr '" << GetName() << "' is not linked");
            return;
        }
        m_pQueue->UnlinkFromSink();
        m_isLinked = false;
    }

    bool FakeSinkBintr::SetSyncSettings(bool sync, bool async)
    {
        LOG_FUNC();
        
        if (IsLinked())
        {
            LOG_ERROR("Unable to set Sync/Async Settings for OverlaySinkBintr '" << GetName() 
                << "' as it's currently linked");
            return false;
        }
        m_sync = sync;
        m_async = async;
        
        m_pFakeSink->SetAttribute("sync", m_sync);
        m_pFakeSink->SetAttribute("async", m_async);
        
        return true;
    }
    
    //-------------------------------------------------------------------------

    OverlaySinkBintr::OverlaySinkBintr(const char* name, uint overlayId, uint displayId, 
        uint depth, uint offsetX, uint offsetY, uint width, uint height)
        : SinkBintr(name, true, false) // sync, async
        , m_qos(FALSE)
        , m_overlayId(overlayId)
        , m_displayId(displayId)
        , m_depth(depth)
        , m_offsetX(offsetX)
        , m_offsetY(offsetY)
        , m_width(width)
        , m_height(height)
    {
        LOG_FUNC();
        
        m_pOverlay = DSL_ELEMENT_NEW(NVDS_ELEM_SINK_OVERLAY, "sink-bin-overlay");
        
        AddChild(m_pOverlay);
    }
    
    OverlaySinkBintr::~OverlaySinkBintr()
    {
        LOG_FUNC();
    }

    bool OverlaySinkBintr::LinkAll()
    {
        LOG_FUNC();
        
        if (m_isLinked)
        {
            LOG_ERROR("OverlaySinkBintr '" << GetName() << "' is already linked");
            return false;
        }
        if (!m_pOverlay)
        {
            LOG_INFO("Creating new Sink Overlay Element on LinkAll for Sink'" << GetName());
            m_pOverlay = DSL_ELEMENT_NEW(NVDS_ELEM_SINK_OVERLAY, "sink-bin-overlay");
            
            AddChild(m_pOverlay);
        }
        m_pOverlay->SetAttribute("overlay", m_overlayId);
        m_pOverlay->SetAttribute("display-id", m_displayId);
        m_pOverlay->SetAttribute("max-lateness", -1);
        m_pOverlay->SetAttribute("sync", m_sync);
        m_pOverlay->SetAttribute("async", m_async);
        m_pOverlay->SetAttribute("qos", m_qos);
        m_pOverlay->SetAttribute("overlay-x", m_offsetX);
        m_pOverlay->SetAttribute("overlay-y", m_offsetY);
        m_pOverlay->SetAttribute("overlay-w", m_width);
        m_pOverlay->SetAttribute("overlay-h", m_height);
        if (!m_pQueue->LinkToSink(m_pOverlay))
        {
            return false;
        }
        m_isLinked = true;
        return true;
    }
    
    void OverlaySinkBintr::UnlinkAll()
    {
        LOG_FUNC();
        
        if (!m_isLinked)
        {
            LOG_ERROR("OverlaySinkBintr '" << GetName() << "' is not linked");
            return;
        }
        m_pQueue->UnlinkFromSink();
        RemoveChild(m_pOverlay);
        m_pOverlay = nullptr;
        m_isLinked = false;
    }

    int OverlaySinkBintr::GetDisplayId()
    {
        LOG_FUNC();
        
        return m_displayId;
    }
    
    bool OverlaySinkBintr::SetDisplayId(int id)
    {
        LOG_FUNC();
        
        if (IsInUse())
        {
            LOG_ERROR("Unable to set Dimensions for OverlaySinkBintr '" << GetName() 
                << "' as it's currently in use");
            return false;
        }

        m_displayId = id;
        m_pOverlay->SetAttribute("display-id", m_displayId);
        
        return true;
    }
    
    void  OverlaySinkBintr::GetOffsets(uint* offsetX, uint* offsetY)
    {
        LOG_FUNC();
        
        *offsetX = m_offsetX;
        *offsetY = m_offsetY;
    }
    
    bool OverlaySinkBintr::SetOffsets(uint offsetX, uint offsetY)
    {
        LOG_FUNC();
        
        if (IsInUse())
        {
            LOG_ERROR("Unable to set Dimensions for OverlaySinkBintr '" << GetName() 
                << "' as it's currently in use");
            return false;
        }

        m_offsetX = offsetX;
        m_offsetY = offsetY;

        m_pOverlay->SetAttribute("overlay-x", m_offsetX);
        m_pOverlay->SetAttribute("overlay-y", m_offsetY);
        
        return true;
    }

    void OverlaySinkBintr::GetDimensions(uint* width, uint* height)
    {
        LOG_FUNC();
        
        *width = m_width;
        *height = m_height;
    }

    bool OverlaySinkBintr::SetDimensions(uint width, uint height)
    {
        LOG_FUNC();
        
        if (IsInUse())
        {
            LOG_ERROR("Unable to set Dimensions for OverlaySinkBintr '" << GetName() 
                << "' as it's currently in use");
            return false;
        }

        m_width = width;
        m_height = height;

        m_pOverlay->SetAttribute("overlay-w", m_width);
        m_pOverlay->SetAttribute("overlay-h", m_height);
        
        return true;
    }

    bool OverlaySinkBintr::SetSyncSettings(bool sync, bool async)
    {
        LOG_FUNC();
        
        if (IsLinked())
        {
            LOG_ERROR("Unable to set Sync/Async Settings for OverlaySinkBintr '" << GetName() 
                << "' as it's currently linked");
            return false;
        }
        m_sync = sync;
        m_async = async;
        
        m_pOverlay->SetAttribute("sync", m_sync);
        m_pOverlay->SetAttribute("async", m_async);

        return true;
    }
    
    //-------------------------------------------------------------------------

    WindowSinkBintr::WindowSinkBintr(const char* name, guint offsetX, guint offsetY, 
        guint width, guint height)
        : SinkBintr(name, true, false)
        , m_qos(false)
        , m_offsetX(offsetX)
        , m_offsetY(offsetY)
        , m_width(width)
        , m_height(height)
    {
        LOG_FUNC();
        
        m_pTransform = DSL_ELEMENT_NEW(NVDS_ELEM_EGLTRANSFORM, "sink-bin-transform");
        m_pEglGles = DSL_ELEMENT_NEW(NVDS_ELEM_SINK_EGL, "sink-bin-eglgles");
        
        m_pEglGles->SetAttribute("window-x", m_offsetX);
        m_pEglGles->SetAttribute("window-y", m_offsetY);
        m_pEglGles->SetAttribute("window-width", m_width);
        m_pEglGles->SetAttribute("window-height", m_height);
        m_pEglGles->SetAttribute("enable-last-sample", false);
        
        m_pEglGles->SetAttribute("max-lateness", -1);
        m_pEglGles->SetAttribute("sync", m_sync);
        m_pEglGles->SetAttribute("async", m_async);
        m_pEglGles->SetAttribute("qos", m_qos);
        
        AddChild(m_pTransform);
        AddChild(m_pEglGles);
    }
    
    WindowSinkBintr::~WindowSinkBintr()
    {
        LOG_FUNC();

        if (IsLinked())
        {    
            UnlinkAll();
        }
    }

    bool WindowSinkBintr::LinkAll()
    {
        LOG_FUNC();
        
        if (m_isLinked)
        {
            LOG_ERROR("OverlaySinkBintr '" << GetName() << "' is already linked");
            return false;
        }
        if (!m_pQueue->LinkToSink(m_pTransform) or
            !m_pTransform->LinkToSink(m_pEglGles))
        {
            return false;
        }
        m_isLinked = true;
        return true;
    }
    
    void WindowSinkBintr::UnlinkAll()
    {
        LOG_FUNC();
        
        if (!m_isLinked)
        {
            LOG_ERROR("OverlaySinkBintr '" << GetName() << "' is not linked");
            return;
        }
        m_pQueue->UnlinkFromSink();
        m_pTransform->UnlinkFromSink();
        m_isLinked = false;
    }

    void  WindowSinkBintr::GetOffsets(uint* offsetX, uint* offsetY)
    {
        LOG_FUNC();
        
        *offsetX = m_offsetX;
        *offsetY = m_offsetY;
    }
    
    bool WindowSinkBintr::SetOffsets(uint offsetX, uint offsetY)
    {
        LOG_FUNC();
        
        if (IsInUse())
        {
            LOG_ERROR("Unable to set Dimensions for WindowSinkBintr '" << GetName() 
                << "' as it's currently in use");
            return false;
        }

        m_offsetX = offsetX;
        m_offsetY = offsetY;

        m_pEglGles->SetAttribute("window-x", m_offsetX);
        m_pEglGles->SetAttribute("window-y", m_offsetY);
        
        return true;
    }

    void WindowSinkBintr::GetDimensions(uint* width, uint* height)
    {
        LOG_FUNC();
        
        *width = m_width;
        *height = m_height;
    }

    bool WindowSinkBintr::SetDimensions(uint width, uint height)
    {
        LOG_FUNC();
        
        if (IsInUse())
        {
            LOG_ERROR("Unable to set Dimensions for WindowSinkBintr '" << GetName() 
                << "' as it's currently in use");
            return false;
        }

        m_width = width;
        m_height = height;

        m_pEglGles->SetAttribute("window-width", m_width);
        m_pEglGles->SetAttribute("window-height", m_height);
        
        return true;
    }

    bool WindowSinkBintr::SetSyncSettings(bool sync, bool async)
    {
        LOG_FUNC();
        
        if (IsLinked())
        {
            LOG_ERROR("Unable to set Sync/Async Settings for WindowSinkBintr '" << GetName() 
                << "' as it's currently linked");
            return false;
        }
        m_sync = sync;
        m_async = async;
        
        m_pEglGles->SetAttribute("sync", m_sync);
        m_pEglGles->SetAttribute("async", m_async);

        return true;
    }
    
    //-------------------------------------------------------------------------
    
    EncodeSinkBintr::EncodeSinkBintr(const char* name,
        uint codec, uint container, uint bitRate, uint interval)
        : SinkBintr(name, true, false)
        , m_codec(codec)
        , m_bitRate(bitRate)
        , m_interval(interval)
        , m_container(container)
    {
        LOG_FUNC();
        
        m_pTransform = DSL_ELEMENT_NEW(NVDS_ELEM_VIDEO_CONV, "encode-sink-bin-transform");
        m_pCapsFilter = DSL_ELEMENT_NEW(NVDS_ELEM_CAPS_FILTER, "encode-sink-bin-caps-filter");
        m_pTransform->SetAttribute("gpu-id", m_gpuId);

        GstCaps* pCaps(NULL);
        switch (codec)
        {
        case DSL_CODEC_H264 :
            m_pEncoder = DSL_ELEMENT_NEW(NVDS_ELEM_ENC_H264_HW, "encode-sink-bin-encoder");
            m_pEncoder->SetAttribute("bitrate", m_bitRate);
            m_pEncoder->SetAttribute("iframeinterval", m_interval);
            m_pEncoder->SetAttribute("bufapi-version", true);
            m_pParser = DSL_ELEMENT_NEW("h264parse", "encode-sink-bin-parser");
            pCaps = gst_caps_from_string("video/x-raw(memory:NVMM), format=I420");
            break;
        case DSL_CODEC_H265 :
            m_pEncoder = DSL_ELEMENT_NEW(NVDS_ELEM_ENC_H265_HW, "encode-sink-bin-encoder");
            m_pEncoder->SetAttribute("bitrate", m_bitRate);
            m_pEncoder->SetAttribute("iframeinterval", m_interval);
            m_pEncoder->SetAttribute("bufapi-version", true);
            m_pParser = DSL_ELEMENT_NEW("h265parse", "encode-sink-bin-parser");
            pCaps = gst_caps_from_string("video/x-raw(memory:NVMM), format=I420");
            break;
        case DSL_CODEC_MPEG4 :
            m_pEncoder = DSL_ELEMENT_NEW(NVDS_ELEM_ENC_MPEG4, "encode-sink-bin-encoder");
            m_pParser = DSL_ELEMENT_NEW("mpeg4videoparse", "encode-sink-bin-parser");
            pCaps = gst_caps_from_string("video/x-raw, format=I420");
            break;
        default:
            LOG_ERROR("Invalid codec = '" << codec << "' for new Sink '" << name << "'");
            throw;
        }

        m_pCapsFilter->SetAttribute("caps", pCaps);
        gst_caps_unref(pCaps);

        AddChild(m_pTransform);
        AddChild(m_pCapsFilter);
        AddChild(m_pEncoder);
        AddChild(m_pParser);
    }

    void  EncodeSinkBintr::GetVideoFormats(uint* codec, uint* container)
    {
        LOG_FUNC();
        
        *codec = m_codec;
        *container = m_container;
    }
    
    void  EncodeSinkBintr::GetEncoderSettings(uint* bitRate, uint* interval)
    {
        LOG_FUNC();
        
        *bitRate = m_bitRate;
        *interval = m_interval;
    }
    
    bool EncodeSinkBintr::SetEncoderSettings(uint bitRate, uint interval)
    {
        LOG_FUNC();
        
        if (IsInUse())
        {
            LOG_ERROR("Unable to set Encoder Settings for FileSinkBintr '" << GetName() 
                << "' as it's currently in use");
            return false;
        }

        m_bitRate = bitRate;
        m_interval = interval;

        if (m_codec == DSL_CODEC_H264 or m_codec == DSL_CODEC_H265)
        {
            m_pEncoder->SetAttribute("bitrate", m_bitRate);
            m_pEncoder->SetAttribute("iframeinterval", m_interval);
        }
        return true;
    }
    
    bool EncodeSinkBintr::SetGpuId(uint gpuId)
    {
        LOG_FUNC();
        
        if (IsInUse())
        {
            LOG_ERROR("Unable to set GPU ID for FileSinkBintr '" << GetName() 
                << "' as it's currently in use");
            return false;
        }

        m_gpuId = gpuId;
        LOG_DEBUG("Setting GPU ID to '" << gpuId << "' for FileSinkBintr '" << GetName() << "'");

        m_pTransform->SetAttribute("gpu-id", m_gpuId);
        
        return true;
    }

    //-------------------------------------------------------------------------
    
    FileSinkBintr::FileSinkBintr(const char* name, const char* filepath, 
        uint codec, uint container, uint bitRate, uint interval)
        : EncodeSinkBintr(name, codec, container, bitRate, interval)
    {
        LOG_FUNC();
        
        m_pFileSink = DSL_ELEMENT_NEW(NVDS_ELEM_SINK_FILE, "file-sink-bin");

        m_pFileSink->SetAttribute("location", filepath);
        m_pFileSink->SetAttribute("sync", m_sync);
        m_pFileSink->SetAttribute("async", m_async);
        
        switch (container)
        {
        case DSL_CONTAINER_MP4 :
            m_pContainer = DSL_ELEMENT_NEW(NVDS_ELEM_MUX_MP4, "encode-sink-bin-container");        
            break;
        case DSL_CONTAINER_MKV :
            m_pContainer = DSL_ELEMENT_NEW(NVDS_ELEM_MKV, "encode-sink-bin-container");        
            break;
        default:
            LOG_ERROR("Invalid container = '" << container << "' for new Sink '" << name << "'");
            throw;
        }

        AddChild(m_pContainer);
        AddChild(m_pFileSink);
    }
    
    FileSinkBintr::~FileSinkBintr()
    {
        LOG_FUNC();

        if (IsLinked())
        {    
            UnlinkAll();
        }
    }

    bool FileSinkBintr::LinkAll()
    {
        LOG_FUNC();
        
        if (m_isLinked)
        {
            LOG_ERROR("FileSinkBintr '" << GetName() << "' is already linked");
            return false;
        }
        if (!m_pQueue->LinkToSink(m_pTransform) or
            !m_pTransform->LinkToSink(m_pCapsFilter) or
            !m_pCapsFilter->LinkToSink(m_pEncoder) or
            !m_pEncoder->LinkToSink(m_pParser) or
            !m_pParser->LinkToSink(m_pContainer) or
            !m_pContainer->LinkToSink(m_pFileSink))
        {
            return false;
        }
        m_isLinked = true;
        return true;
    }
    
    void FileSinkBintr::UnlinkAll()
    {
        LOG_FUNC();
        
        if (!m_isLinked)
        {
            LOG_ERROR("FileSinkBintr '" << GetName() << "' is not linked");
            return;
        }
        m_pContainer->UnlinkFromSink();
        m_pParser->UnlinkFromSink();
        m_pEncoder->UnlinkFromSink();
        m_pCapsFilter->UnlinkFromSink();
        m_pTransform->UnlinkFromSink();
        m_pQueue->UnlinkFromSink();
        m_isLinked = false;
    }

    bool FileSinkBintr::SetSyncSettings(bool sync, bool async)
    {
        LOG_FUNC();
        
        if (IsLinked())
        {
            LOG_ERROR("Unable to set Sync/Async Settings for FileSinkBintr '" << GetName() 
                << "' as it's currently linked");
            return false;
        }
        m_sync = sync;
        m_async = async;
        
        m_pFileSink->SetAttribute("sync", m_sync);
        m_pFileSink->SetAttribute("async", m_async);

        return true;
    }
    
    //-------------------------------------------------------------------------
    
    RecordSinkBintr::RecordSinkBintr(const char* name, const char* outdir, 
        uint codec, uint container, uint bitRate, uint interval, dsl_record_client_listener_cb clientListener)
        : EncodeSinkBintr(name, codec, container, bitRate, interval)
        , RecordMgr(name, outdir, container, clientListener)
    {
        LOG_FUNC();
        
    }
    
    RecordSinkBintr::~RecordSinkBintr()
    {
        LOG_FUNC();

        if (IsLinked())
        {    
            UnlinkAll();
        }
    }

    bool RecordSinkBintr::LinkAll()
    {
        LOG_FUNC();
        
        if (m_isLinked)
        {
            LOG_ERROR("RecordSinkBintr '" << GetName() << "' is already linked");
            return false;
        }

        CreateContext();
        
        m_pRecordBin = DSL_NODETR_NEW("record-bin");
        m_pRecordBin->SetGstObject(GST_OBJECT(m_pContext->recordbin));
            
        AddChild(m_pRecordBin);

        if (!m_pQueue->LinkToSink(m_pTransform) or
            !m_pTransform->LinkToSink(m_pCapsFilter) or
            !m_pCapsFilter->LinkToSink(m_pEncoder) or
            !m_pEncoder->LinkToSink(m_pParser))
        {
            return false;
        }
        GstPad* srcPad = gst_element_get_static_pad(m_pParser->GetGstElement(), "src");
        GstPad* sinkPad = gst_element_get_static_pad(m_pRecordBin->GetGstElement(), "sink");
        
        if (gst_pad_link(srcPad, sinkPad) != GST_PAD_LINK_OK)
        {
            LOG_ERROR("Failed to link parser to record-bin new RecordSinkBintr '" << GetName() << "'");
            return false;
        }
        m_isLinked = true;
        return true;
    }
    
    void RecordSinkBintr::UnlinkAll()
    {
        LOG_FUNC();
        
        if (!m_isLinked)
        {
            LOG_ERROR("RecordSinkBintr '" << GetName() << "' is not linked");
            return;
        }
        GstPad* srcPad = gst_element_get_static_pad(m_pParser->GetGstElement(), "src");
        GstPad* sinkPad = gst_element_get_static_pad(m_pRecordBin->GetGstElement(), "sink");
        
        gst_pad_unlink(srcPad, sinkPad);

        m_pEncoder->UnlinkFromSink();
        m_pCapsFilter->UnlinkFromSink();
        m_pTransform->UnlinkFromSink();
        m_pQueue->UnlinkFromSink();
        
        RemoveChild(m_pRecordBin);
        
        m_pRecordBin = nullptr;
        DestroyContext();
        
        m_isLinked = false;
    }

    
    bool RecordSinkBintr::SetSyncSettings(bool sync, bool async)
    {
        LOG_FUNC();
        
        if (IsLinked())
        {
            LOG_ERROR("Unable to set Sync/Async Settings for FileSinkBintr '" << GetName() 
                << "' as it's currently linked");
            return false;
        }
        m_sync = sync;
        m_async = async;

        // TODO set sync/async for file element owned by context??
        return true;
    }

    //******************************************************************************************
    
    RtspSinkBintr::RtspSinkBintr(const char* name, const char* host, uint udpPort, uint rtspPort,
         uint codec, uint bitRate, uint interval)
        : SinkBintr(name, false, false)
        , m_host(host)
        , m_udpPort(udpPort)
        , m_rtspPort(rtspPort)
        , m_codec(codec)
        , m_bitRate(bitRate)
        , m_interval(interval)
        , m_pServer(NULL)
        , m_pFactory(NULL)
    {
        LOG_FUNC();
        
        m_pUdpSink = DSL_ELEMENT_NEW("udpsink", "rtsp-sink-bin");
        m_pTransform = DSL_ELEMENT_NEW(NVDS_ELEM_VIDEO_CONV, "rtsp-sink-bin-transform");
        m_pCapsFilter = DSL_ELEMENT_NEW(NVDS_ELEM_CAPS_FILTER, "rtsp-sink-bin-caps-filter");

        m_pUdpSink->SetAttribute("host", m_host.c_str());
        m_pUdpSink->SetAttribute("port", m_udpPort);
        m_pUdpSink->SetAttribute("sync", m_sync);
        m_pUdpSink->SetAttribute("async", m_async);

        GstCaps* pCaps = gst_caps_from_string("video/x-raw(memory:NVMM), format=I420");
        m_pCapsFilter->SetAttribute("caps", pCaps);
        gst_caps_unref(pCaps);
        
        std::string codecString;
        switch (codec)
        {
        case DSL_CODEC_H264 :
            m_pEncoder = DSL_ELEMENT_NEW(NVDS_ELEM_ENC_H264_HW, "rtsp-sink-bin-h264-encoder");
            m_pParser = DSL_ELEMENT_NEW("h264parse", "rtsp-sink-bin-h264-parser");
            m_pPayloader = DSL_ELEMENT_NEW("rtph264pay", "rtsp-sink-bin-h264-payloader");
            codecString.assign("H264");
            break;
        case DSL_CODEC_H265 :
            m_pEncoder = DSL_ELEMENT_NEW(NVDS_ELEM_ENC_H265_HW, "rtsp-sink-bin-h265-encoder");
            m_pParser = DSL_ELEMENT_NEW("h265parse", "rtsp-sink-bin-h265-parser");
            m_pPayloader = DSL_ELEMENT_NEW("rtph265pay", "rtsp-sink-bin-h265-payloader");
            codecString.assign("H265");
            break;
        default:
            LOG_ERROR("Invalid codec = '" << codec << "' for new Sink '" << name << "'");
            throw;
        }

        m_pEncoder->SetAttribute("bitrate", m_bitRate);
        m_pEncoder->SetAttribute("iframeinterval", m_interval);
        m_pEncoder->SetAttribute("preset-level", true);
        m_pEncoder->SetAttribute("insert-sps-pps", true);
        m_pEncoder->SetAttribute("bufapi-version", true);
        
        // Setup the GST RTSP Server
        m_pServer = gst_rtsp_server_new();
        g_object_set(m_pServer, "service", std::to_string(m_rtspPort).c_str(), NULL);

        std::string udpSrc = "(udpsrc name=pay0 port=" + std::to_string(m_udpPort) + 
            " caps=\"application/x-rtp, media=video, clock-rate=90000, encoding-name=" +
            codecString + ", payload=96 \")";
        
        // Create a nw RTSP Media Factory and set the launch settings
        // to the UDP source defined above
        m_pFactory = gst_rtsp_media_factory_new();
        gst_rtsp_media_factory_set_launch(m_pFactory, udpSrc.c_str());

        LOG_INFO("UDP Src for RtspSinkBintr '" << GetName() << "' = " << udpSrc);

        // Get a handle to the Mount-Points object from the new RTSP Server
        GstRTSPMountPoints* pMounts = gst_rtsp_server_get_mount_points(m_pServer);

        // Attach the RTSP Media Factory to the mount-point-path in the mounts object.
        std::string uniquePath = "/" + GetName();
        gst_rtsp_mount_points_add_factory(pMounts, uniquePath.c_str(), m_pFactory);
        g_object_unref(pMounts);

        AddChild(m_pUdpSink);
        AddChild(m_pTransform);
        AddChild(m_pCapsFilter);
        AddChild(m_pEncoder);
        AddChild(m_pParser);
        AddChild(m_pPayloader);
    }
    
    RtspSinkBintr::~RtspSinkBintr()
    {
        LOG_FUNC();

        if (IsLinked())
        {    
            UnlinkAll();
        }
    }

    bool RtspSinkBintr::LinkAll()
    {
        LOG_FUNC();
        
        if (m_isLinked)
        {
            LOG_ERROR("RtspSinkBintr '" << GetName() << "' is already linked");
            return false;
        }
        
        if (!m_pQueue->LinkToSink(m_pTransform) or
            !m_pTransform->LinkToSink(m_pCapsFilter) or
            !m_pCapsFilter->LinkToSink(m_pEncoder) or
            !m_pEncoder->LinkToSink(m_pParser) or
            !m_pParser->LinkToSink(m_pPayloader) or
            !m_pPayloader->LinkToSink(m_pUdpSink))
        {
            return false;
        }

        // Attach the server to the Main loop context. Server will accept
        // connections the once main loop has been started
        m_pServerSrcId = gst_rtsp_server_attach(m_pServer, NULL);

        m_isLinked = true;
        return true;
    }
    
    void RtspSinkBintr::UnlinkAll()
    {
        LOG_FUNC();
        
        if (!m_isLinked)
        {
            LOG_ERROR("RtspSinkBintr '" << GetName() << "' is not linked");
            return;
        }
        if (m_pServerSrcId)
        {
            // Remove (destroy) the source from the Main loop context
            g_source_remove(m_pServerSrcId);
            m_pServerSrcId = 0;
        }
        
        m_pPayloader->UnlinkFromSink();
        m_pParser->UnlinkFromSink();
        m_pEncoder->UnlinkFromSink();
        m_pCapsFilter->UnlinkFromSink();
        m_pTransform->UnlinkFromSink();
        m_pQueue->UnlinkFromSink();
        m_isLinked = false;
    }
    
    void RtspSinkBintr::GetServerSettings(uint* udpPort, uint* rtspPort, uint* codec)
    {
        LOG_FUNC();
        
        *udpPort = m_udpPort;
        *rtspPort = m_rtspPort;
        *codec = m_codec;
    }
    
    void  RtspSinkBintr::GetEncoderSettings(uint* bitRate, uint* interval)
    {
        LOG_FUNC();
        
        *bitRate = m_bitRate;
        *interval = m_interval;
    }
    
    bool RtspSinkBintr::SetEncoderSettings(uint bitRate, uint interval)
    {
        LOG_FUNC();
        
        if (IsLinked())
        {
            LOG_ERROR("Unable to set Encoder Settings for FileSinkBintr '" << GetName() 
                << "' as it's currently linked");
            return false;
        }

        m_bitRate = bitRate;
        m_interval = interval;

        if (m_codec == DSL_CODEC_H264 or m_codec == DSL_CODEC_H265)
        {
            m_pEncoder->SetAttribute("bitrate", m_bitRate);
            m_pEncoder->SetAttribute("iframeinterval", m_interval);
        }
        return true;
    }
    
    bool RtspSinkBintr::SetSyncSettings(bool sync, bool async)
    {
        LOG_FUNC();
        
        if (IsLinked())
        {
            LOG_ERROR("Unable to set Sync/Async Settings for FileSinkBintr '" << GetName() 
                << "' as it's currently linked");
            return false;
        }
        m_sync = sync;
        m_async = async;
        
        m_pUdpSink->SetAttribute("sync", m_sync);
        m_pUdpSink->SetAttribute("async", m_async);

        return true;
    }
    
}    