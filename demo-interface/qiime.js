(function(window, qiime, Promise, undefined){
    var document = window.document;    
    function XMLHTTPREQUEST(method, url) {
        var d = Promise.defer()
        var xhr = new XMLHttpRequest();
        xhr.open(method, url, true);
        xhr.onload = function (e) {
            if(xhr.readyState === 4) {
                if (xhr.status === 200) {
                    d.resolve(JSON.parse(xhr.responseText));
                } else {
                    d.reject(new Error(e))
                }
            }
        };
        xhr.onerror = function (e) {
            d.reject(new Error(e))
        };
        xhr.send();
        return d.promise
    }
    qiime.connect = function(hostname) {    
        var listeners = [];
        function NOTIFY() {
            listeners.forEach(function(cb) { cb(); });
        }
        var log = [];
        function LOG(msg, req, res) {
            log.push({message:msg, request: req, response: res});
            NOTIFY();
        }
        
        function GET(path, args) {
            var url = hostname + path;
            promise = XMLHTTPREQUEST('get', url)
            promise.then(function(res) { LOG("GET: "+ url, {}, res); }, function(error) { LOG("ERROR on GET: "+url, {}, error.message) });
            return promise
        }
        function PUT(path, args) {

        }
        function POST(path, args) {

        }
        function DELETE(path) {

        }
        
        function Artifact(uri) {
            return GET(uri).then(function(response) {
                return Promise.Promise(function(resolve) {
                    var artifact = {}
                    artifact.id = response.resource;
                    artifact.type = response.type;
                    artifact.name = response.name;
                    
                    resolve(artifact);
                });
            });
        }

        function Job(uri) {
            var job = {}
            
            return Promise.Promise(function(r) { r(uri + ' :-)'); });
        }

        function Study(uri) {
            return GET(uri).then(function(response){
               return Promise.Promise(function(resolve){ 
                    var study = {}

                    study.id = response.resource;
                    study.name = response.name;
                    study.description = response.description;
                    study.created = response.created;
                    study.log = [];
                    study.jobs = [];
                    study.artifacts = [];

                    study.createArtifact = function() {

                    }

                    study.linkArtifact = function() {

                    }

                    study.deleteArtifact = function() {

                    }

                    study.createJob = function() {

                    }

                    study.deleteJob = function() {

                    }

                    Promise.all([
                        GET(uri+'/artifacts').then(function(r) { return Promise.all(r.artifacts.map(function(v){ return Artifact(v); })); }),
                        GET(uri+'/jobs').then(function(r) { return Promise.all(r.jobs.map(function(v){ return Job(v); })); }),
                    ]).spread(function(artifacts, jobs) {
                        study.artifacts = artifacts;
                        study.jobs = jobs;
                        resolve(study);
                    });
                }); 
            });
        }
        
        return GET('/system').then(function(system){
            return Promise.all([
                GET('/system/plugins/all/methods'),
                GET('/system/plugins/all/types'),
                GET('/studies'),
            ]).spread(function(methods, types, studies) {
                return Promise.Promise(function(resolve){
                    var connection = {};
                    connection.version = system.version;
                    connection.methods = methods.methods;
                    connection.types = types.types;
                
                    connection.createStudy = function() {

                    }
                    connection.deleteStudy = function() {

                    }
                    connection.listen = function(callback) {
                        listeners.push(function() { callback(connection); });
                    }
                    connection.log = log;
                    Promise.all(studies.studies.map(function(value) {
                        return Study(value);
                    })).then(function(studies) {
                        connection.studies = studies
                        resolve(connection)
                    });
                }); 
            });
            
            
            
        });
    }
})(window, window.qiime = window.qiime || {}, Q);