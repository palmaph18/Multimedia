// Estados
let estadoActual = 'ESPERANDO_ACTIVACION'; 
let empresaActual = '';

// Funcion para iniciar la escucha de voz
function listen() {
  let inputArea = document.getElementById('input-area');
  let outputArea = document.getElementById('output-area');

  // Inicializamos el reconocimiento de voz
  var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  var recognition = new SpeechRecognition();
  
  recognition.lang = "es-MX";
  recognition.continuous = false; 
  recognition.start();

  recognition.onresult = function(event) {
    let transcript = event.results[0][0].transcript.toLowerCase().trim();
    console.log("Usuario dijo: ", transcript);
    
    if(inputArea) inputArea.innerHTML = "Tú: " + transcript;

    // Máquina de estados para el flujo conversacional
    switch (estadoActual) {
      
      // NIVEL 0: Activación
      case 'ESPERANDO_ACTIVACION':
        if (transcript.includes("finanzas")) {
          estadoActual = 'ESPERANDO_EMPRESA';
          // Eliminamos la petición del ticker, ahora es 100% natural
          responder(outputArea, "Dime el nombre de la empresa que quieres revisar."); 
        }
        break;

      // NIVEL 1: Categoría
      case 'ESPERANDO_EMPRESA':
        empresaActual = transcript; 
        estadoActual = 'ESPERANDO_CATEGORIA';
        responder(outputArea, `He registrado ${empresaActual}. ¿Quieres ver sus estadísticas o quieres ver sus gráficas?`); 
        break;

      // NIVEL 2: Discriminación
      case 'ESPERANDO_CATEGORIA':
        if (transcript.includes("estadística") || transcript.includes("estadísticas")) {
          estadoActual = 'ESPERANDO_ESTADISTICA';
          responder(outputArea, "¿Te interesa saber su market cap y valoración, o prefieres ver su nivel de deuda?"); 
        } else if (transcript.includes("gráfica") || transcript.includes("gráficas")) {
          estadoActual = 'ESPERANDO_GRAFICA';
          responder(outputArea, "¿Gráfica del día de hoy, de hace una semana o de hace un año?"); 
        } else {
          responder(outputArea, "Por favor, especifica si prefieres estadísticas o gráficas.");
        }
        break;

      // NIVEL 3A: Resolución de Estadísticas (Búsqueda directa en Google)
      case 'ESPERANDO_ESTADISTICA':
        if (transcript.includes("market") || transcript.includes("cap") || transcript.includes("valoración") || transcript.includes("sobrevalorada")) { 
          responder(outputArea, `Buscando la valoración de ${empresaActual} en Google...`);
          // Armamos una búsqueda específica para forzar la respuesta rápida de Google/IA
          let query = encodeURIComponent(`market cap valoracion de ${empresaActual}`);
          window.open(`https://www.google.com/search?q=${query}`, '_blank');
          reiniciarConversacion();
        } else if (transcript.includes("deuda") || transcript.includes("financiera")) { 
          responder(outputArea, `Buscando los datos de deuda para ${empresaActual} en Google...`);
          let query = encodeURIComponent(`nivel de deuda financiera de ${empresaActual}`);
          window.open(`https://www.google.com/search?q=${query}`, '_blank');
          reiniciarConversacion();
        } else {
           responder(outputArea, "Dime si buscas valoración o deuda.");
        }
        break;

      // NIVEL 3B: Resolución de Gráficas (Búsqueda directa en Google)
      case 'ESPERANDO_GRAFICA':
        if (transcript.includes("hoy") || transcript.includes("día")) { 
          responder(outputArea, `Buscando el precio de hoy de ${empresaActual}...`);
          let query = encodeURIComponent(`precio acciones ${empresaActual} hoy`);
          window.open(`https://www.google.com/search?q=${query}`, '_blank');
          reiniciarConversacion();
        } else if (transcript.includes("semana")) { 
          responder(outputArea, `Buscando la gráfica semanal de ${empresaActual}...`);
          let query = encodeURIComponent(`grafica acciones ${empresaActual} ultima semana`);
          window.open(`https://www.google.com/search?q=${query}`, '_blank');
          reiniciarConversacion();
        } else if (transcript.includes("año")) { 
          responder(outputArea, `Buscando la gráfica anual de ${empresaActual}...`);
          let query = encodeURIComponent(`grafica acciones ${empresaActual} ultimo año`);
          window.open(`https://www.google.com/search?q=${query}`, '_blank');
          reiniciarConversacion();
        } else {
          responder(outputArea, "Dime si quieres la gráfica de hoy, de una semana o de un año.");
        }
        break;
    }
  };

  // Reiniciar la escucha automáticamente
  recognition.onend = function() {
    if (estadoActual !== 'ESPERANDO_ACTIVACION') {
      try {
        recognition.start(); 
      } catch(e) {
        console.log("El reconocimiento ya estaba en curso.");
      }
    }
  };
}

// Función auxiliar para actualizar el texto en pantalla y hablar
function responder(elementoDOM, texto) {
  if(elementoDOM) elementoDOM.innerHTML = "Asistente: " + texto;
  hablar(texto);
}

// Función para limpiar la memoria y volver al estado inicial
function reiniciarConversacion() {
  estadoActual = 'ESPERANDO_ACTIVACION';
  empresaActual = '';
}

// Función de síntesis de voz
function hablar(texto) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel(); 
    let utterance = new SpeechSynthesisUtterance(texto);
    utterance.lang = 'es-MX'; 
    window.speechSynthesis.speak(utterance);
  } else {
    console.warn("La síntesis de voz no está soportada en este navegador.");
  }
}
