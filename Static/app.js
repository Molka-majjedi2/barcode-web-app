// const codeReader = new ZXing.BrowserMultiFormatReader();

// let lastCode = "";


// function startScan() {

//     const video = document.getElementById("video");

//     document.getElementById("result").innerHTML =
//         "Scanning...";


//     codeReader.decodeFromVideoDevice(
//         null,
//         video,

//         (result, err) => {

//             if (result) {

//                 let code = String(result.text).trim();

//                 console.log("==========================================");
//                 console.log("ZXING RESULT:", code);
//                 console.log("==========================================");


//                 /*
//                  * Ignore very short false detections
//                  * like 8, 65, 440...
//                  *
//                  * IMPORTANT:
//                  * We don't use a strict 12-14 filter here.
//                  */

//                 if (code.length < 8) {

//                     console.log(
//                         "Ignored short result:",
//                         code
//                     );

//                     return;
//                 }


//                 /*
//                  * Avoid duplicate scan
//                  */

//                 if (code === lastCode) {
//                     return;
//                 }

//                 lastCode = code;


//                 /*
//                  * Display barcode
//                  */

//                 document.getElementById("result").innerHTML =
//                     "Barcode : " + code;


//                 console.log(
//                     "SENDING TO BACKEND:",
//                     code
//                 );


//                 /*
//                  * Search backend
//                  */

//                 fetch(
//                     "/search?code=" +
//                     encodeURIComponent(code)
//                 )

//                 .then(response => response.json())

//                 .then(data => {

//                     console.log(
//                         "BACKEND RESPONSE:",
//                         data
//                     );


//                     if (data.found) {

//                         if (data.url) {

//                             window.open(
//                                 data.url,
//                                 "_blank"
//                             );

//                         }


//                         document.getElementById("result").innerHTML = `

//                             <h3>
//                                 ${data.name || "Product"}
//                             </h3>

//                             <p>
//                                 <strong>Barcode :</strong>
//                                 ${code}
//                             </p>

//                             <p>
//                                 <strong>Article :</strong>
//                                 ${data.article || "-"}
//                             </p>

//                             <p>
//                                 <strong>Category :</strong>
//                                 ${data.category || "-"}
//                             </p>

//                             <p>
//                                 <strong>ID Product :</strong>
//                                 ${data.id_product || "-"}
//                             </p>

//                             <p>
//                                 Opening website...
//                             </p>

//                         `;


//                     } else {

//                         document.getElementById("result").innerHTML = `

//                             <h3>
//                                 Barcode not found
//                             </h3>

//                             <p>
//                                 <strong>Barcode :</strong>
//                                 ${code}
//                             </p>

//                             <p>
//                                 Ce code n'existe pas dans
//                                 la base de données.
//                             </p>

//                         `;

//                     }


//                     /*
//                      * Stop scanner
//                      */

//                     codeReader.reset();

//                 })

//                 .catch(error => {

//                     console.error(
//                         "BACKEND ERROR:",
//                         error
//                     );

//                     document.getElementById("result").innerHTML =
//                         "Erreur serveur";

//                 });

//             }


//             /*
//              * Ignore normal ZXing errors
//              */

//             if (
//                 err &&
//                 err.name !== "NotFoundException"
//             ) {

//                 console.log(
//                     "ZXING ERROR:",
//                     err
//                 );

//             }

//         }
//     );
// }