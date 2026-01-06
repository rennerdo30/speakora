# Issues

## Open Issues
- [ ] **Streaming Context**: The current `translate_audio_stream` processes each text chunk independently. It should maintain context/state for better translation quality.
- [ ] **Security**: Add authentication to API and WebSocket endpoints.
- [ ] **Mobile Support**: Make the Web GUI responsive for mobile.

## Resolved Issues
- ✅ Initial project setup and structure
- ✅ Implement core modules (Phase 1)
- ✅ Achieve 100% test coverage
- ✅ Implement Web GUI (Phase 2)
- ✅ Implement Browser Extension (Phase 3)
- ✅ Dockerization
- ✅ **Memory Usage**: Streaming file processing implemented for offline jobs.
- ✅ **Error Handling**: WebSocket reconnection logic added to extension.
- ✅ **Voice Activity Detection**: Basic RMS-based VAD implemented for streaming.
