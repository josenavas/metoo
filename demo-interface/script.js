(function(window, qiime, Promise, undefined){
    qiime.connect = function(host) {
        connection = (function(){
            function xmlhttprequest(method, url, success, failure) {
                var xhr = new XMLHttpRequest();
                xhr.open(method, url, true);
                xhr.onload = function (e) {
                    if(xhr.readyState === 4) {
                        if (xhr.status === 200) {
                            success(JSON.parse(xhr.responseText));
                        } else {
                            failure(new Error(e))
                        }
                    }
                };
                xhr.onerror = function (e) {
                    failure(new Error(e))
                };
                xhr.send();
            }

            var c = {};
            c.get = function(path, parameters) {
                var uri = host + path
                var first_iter = true;
                for(var name in parameters) {
                    if (parameters.hasOwnProperty(name)) {
                        if(first_iter) {
                            uri += '?';
                            first_iter = false;
                        } else {
                            uri += '&';
                        }
                        uri += encodeURIComponent(name) + "=";
                        uri += encodeURIComponent(parameters[name]);
                    }
                }
                var d = Promise.defer()
                xmlhttprequest('GET', uri, d.resolve, d.reject)
                return d.promise;
            }

            c.put = function() {

            }

            c.post = function() {

            }

            c.delete = function() {

            }

            return c;
        })()

        var api = {};

        api.create_artifact = function(fp) {
        }

        api.delete_artifact = function(artifact) {

        }

        api.update_artifact = function(artifact) {

        }

        api.artifact_info = function(artifact) {

        }

        api.list_methods = function(plugin) {

        }

        api.list_plugins = function() {
            return connection.get('/api/list_plugins')
        }

        api.method_info = function(method) {

        }

        return api;
    }
})(window, window.qiime = window.qiime || {}, Q);
