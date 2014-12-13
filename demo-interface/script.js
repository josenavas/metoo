(function(window, qiime, Promise, undefined){
    qiime.connect = function(host) {
        connection = (function(){
            function xmlhttprequest(method, url) {
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

            var c = {};
            c.get = function(path, parameters) {
                var url = host + path
                var first_iter = true;
                for(var name in parameters) {
                    if (parameters.hasOwnProperty(name)) {
                        if(first_iter) {
                            url += '?';
                            first_iter = false;
                        } else {
                            url += '&';
                        }
                        url += encodeURIComponent(name) + "=";
                        url += encodeURIComponent(parameters[name]);
                    }
                }
                return xmlhttprequest('GET', url, d.resolve, d.reject)
            }

            c.put = function() {

            }

            c.post = function() {

            }

            c.delete = function() {

            }

            return c;
        })()

        function make_listen(resource) {

        }

        function reactive_property(resource, property, formatter) {
            if(!formatter) formatter = function(g, s){ if(g) s=g; return s; };
            if(!resource.api) resource.api = {};
            if(!resource.notifiers) resource.notifiers = [];
            if(!resource.listeners) resource.listeners = {};
            if(!resource.api.listen) {
                resource.api.listen = function(prop, callback) {
                    resource.listeners[prop].append(callback);
                }
            }
            var listeners = resource.listeners[property] = [];

            var value = undefined;
            resource.notifiers.push(function(response) {
                if(JSON.stringify(response[property]) != JSON.stringify(value)) {
                    for(var i=0; i<listeners.length; i++) {
                        value = response[property]
                        listeners[i](value)
                    }
                }
            })
            Object.defineProperty(resource.api, property, {
                enumerable: true,
                get: function() {

                },
                set: function(v) {
                    args = {};
                    args[property] = formatter(undefined, v);
                    connection.put(resource.uri, args).then(function(){
                        resource.update()
                    })
                }
            })
        }


        function study(uri) {
            function artifact(uri) {
                var artifact = {};

                return artifact;
            }

            function job(uri) {
                function time(to, from) {
                    if(from) {
                        t = v.replace('-', '/').split('.')
                        d = new Date(t[0])
                        d.setMilliseconds(Math.round(t[1]/1000))
                        return d;
                    } else {

                    }
                }
                var job = {};
                job.uri = uri;
                job.fetcher = function fetcher() {
                    connection.get(job.uri)
                    window.setTimeout(fetcher, 1000)
                }
                reactive_property(job, 'status');
                reactive_property(job, 'submitted', time);
                reactive_property(job, 'completed', time);
                reactive_property(job, 'inputs');
                reactive_property(job, 'outputs');
                return job.api;
            }

            var study = {};

            study.artifacts = function() {

                return study;
            }

            study.add_artifact = function() {

                return study;
            }

            study.remove_artifact = function() {

                return study;
            }

            study.jobs = function() {

                return study;
            }

            study.submit_job = function() {

            }

            return study;
        }




        var api = {};

        api.studies = function() {

        }

        api.system = function() {

        }

        api.method_info = function() {

        }

        api.type_info = function() {

        }

        api.listen = function(property, )

        return api;
    }
})(window, window.qiime = window.qiime || {}, Q);
