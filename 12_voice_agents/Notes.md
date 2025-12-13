Types:
1. Speech to Speech (s2s) - native audio handling 
user audio => app => agent(s2s model)(tool call(function, search, handoff)) => app => agent audio
i. low latency systems, works realtime


2. Chained Architecture:
user audio => STT(Speech to Text)(convert to text) => LLM(used chat model) => text response => TTS(Text to Speech)(convert to voice)
can use any model, less expensive