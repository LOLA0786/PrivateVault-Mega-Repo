const express = require('express');
const app = express();

app.get('/health', (req,res)=>res.json({ok:true, service:'kb-service'}));

app.get('/modules/:module_id', (req,res) => {
  res.json({
    ok: true,
    message: "module content served",
    module_id: req.params.module_id
  });
});

app.get('/modules/:module_id/*', (req,res) => {
  res.json({
    ok: true,
    path: req.path,
    module_id: req.params.module_id
  });
});

app.listen(8081, ()=>console.log("kb-service running on :8081"));
