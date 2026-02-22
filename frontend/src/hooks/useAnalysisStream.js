// frontend/src/hooks/useAnalysisStream.js

import { useState, useEffect, useCallback } from 'react';

export function useAnalysisStream(analysisId) {
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState({});
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [thoughts, setThoughts] = useState([]);
  const [ws, setWs] = useState(null);
  const [papers, setPapers] = useState([]);

  useEffect(() => {
    if (!analysisId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const websocket = new WebSocket(`${protocol}//localhost:8000/ws/analysis/${analysisId}`);

    websocket.onopen = () => {
      console.log('WebSocket connected');
    };

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case 'status':
          setStatus(message.data);
          break;

        case 'discovery_complete':
          setPapers(message.data.papers);
          setStatus({ status: 'discovery' });
          break;

        case 'step_start':
          setProgress(prev => ({
            ...prev,
            [message.data.step]: { status: 'running', agent: message.data.agent }
          }));
          break;

        case 'step_complete':
          setProgress(prev => ({
            ...prev,
            [message.data.step]: { status: 'complete' }
          }));
          break;

        case 'complete':
          setResults(message.data);
          setStatus({ status: 'completed' });
          break;

        case 'error':
          setError(message.data.error);
          setStatus({ status: 'error' });
          break;
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error');
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, [analysisId]);

  const cancel = useCallback(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: 'cancel' }));
    }
  }, [ws]);

  const selectPaper = useCallback((arxivId) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: 'select_paper', arxiv_id: arxivId }));
    }
  }, [ws]);

  return { status, progress, results, error, thoughts, papers, cancel, selectPaper };
}
