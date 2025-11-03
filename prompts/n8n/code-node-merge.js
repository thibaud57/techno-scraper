// Récupérer les outputs des 2 agents
const soundcloudData = $('Agent SoundCloud').first().json.output || $('Agent SoundCloud').first().json;
const beatportData = $('Agent Beatport').first().json.output || $('Agent Beatport').first().json;

// Fusionner les 2 objets
return {
  ...soundcloudData,
  ...beatportData
};
