function isArray2D(arr) {
    // Verifica si arr es un array
    if (!Array.isArray(arr)) return false;

    // Verifica que cada elemento dentro del array también sea un array
    return arr.every(item => Array.isArray(item));
}

class LoadingElement {
    container = document.getElementById('0');
    style;
    messageId = '_loading_message';
    cssId = '_loading_style';
    id = '_loading_c'
    constructor() {
        this.#setCss();
        this.#createLoading();
    }

    #setCss() {
        if (document.getElementById(this.cssId)) return;
        const css = `
            .loading-container {
                position: fixed;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                background: rgba(0, 0, 0, .25);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all .5s;
            }

            .loading-center {
                width: 10%;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .loader {
                width: 48px;
                height: 48px;
                border: 5px solid #FFF;
                border-bottom-color: transparent;
                border-radius: 50%;
                display: inline-block;
                box-sizing: border-box;
                animation: rotation 1s linear infinite;
            }

            .loading-container-hidden {
                z-index: -1;
                background: transparent;
            }

            @media screen and (max-width: 1280px) {
                .loading-center {
                    width: 20%;
                }
            }

            @media screen and (max-width: 720px) {
                .loading-center {
                    width: 40%;
                    display: block;
                }
            }

            @keyframes rotation {
                0% {
                    transform: rotate(0deg);
                }

                100% {
                    transform: rotate(360deg);
                }
            }
        `
        this.style = document.createElement('style');
        this.style.id = this.cssId;
        this.style.innerHTML = css;
        document.head.appendChild(this.style)
    }

    #createLoading() {
        if (document.getElementById(this.id)) return;
        this.container = document.createElement('div');
        this.container.classList.add('loading-container', 'loading-container-hidden');

        const childCenter = window.document.createElement('div');
        childCenter.classList.add('loading-center');

        childCenter.innerHTML = `
            <div style="color: white" id="${this.messageId}"></div>
            <span class="loader"></span>
        `

        this.container.appendChild(childCenter);
        this.container.id = this.id;
        window.document.body.appendChild(this.container)
    }

    show(message = 'Fetching data from server') {
        window.document.getElementById(this.messageId).innerText = message;
        if (this.container.classList.contains('loading-container-hidden')) {
            this.container.classList.remove('loading-container-hidden')
        }
    }

    hide() {
        if (!this.container.classList.contains('loading-container-hidden')) {
            this.container.classList.add('loading-container-hidden');
            window.document.getElementById(this.id).remove();
            window.document.getElementById(this.cssId).remove();
        }
    }
}

class EVFetch {

    loading;

    constructor(endpoint = 'http://localhost:5000/api') {
        this.endpoint = endpoint;
        this.loading = new LoadingElement();
    }

    // Valida el modelo
    validateModel(model) {
        if (!model || typeof model !== 'string') {
            return {
                error: true,
                message: 'Invalid model provided',
            };
        }
        return null;
    }

    // Valida los datos (cuerpo de la solicitud)
    validateData(data) {
        if (!data || typeof data !== 'object') {
            return {
                error: true,
                message: 'Invalid data provided',
            };
        }
        return null;
    }

    // Configura las cabeceras para la solicitud
    setHeaders(method = 'GET', body = null) {
        const headers = {
            method: method.toUpperCase(),
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json',
            },
        };

        if (body && headers.method !== 'GET') {
            headers.body = JSON.stringify(body);
        }

        return headers;
    }

    // Realiza una solicitud HTTP
    async request(path, method = 'GET', body = null) {
        const apiUrl = `${this.endpoint}/${path}`;
        try {
            this.loading.show();
            const response = await fetch(apiUrl, this.setHeaders(method, body));
            const contentType = response.headers.get('Content-Type');
            this.loading.hide();
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            return await response.text();
        } catch (error) {
            return {
                error: true,
                message: error.message || error,
            };
        }
    }

    // Métodos específicos para la API
    async search(model, params = {}) {
        const error = this.validateModel(model);
        if (error) return error;

        let path = `${model}/search`;

        const querys = [];

        if ('fields' in params && 'length' in params.where) {

            let fields = 'fields='

            if(typeof(params.fields) === 'string') {
                fields +=  params.fields
            } else {
                fields += params.fields.join(',')
            }

            querys.push(fields)
        }

        if ('where' in params && 'length' in params.where) {

            let _where = 'where=';

            if (isArray2D(params.where)) {

                let conditions = []

                params.where.forEach(w => {
                    conditions.push(`(${w.map(w => `'${w}'`).join(',')})`)
                });

                conditions = `(${conditions})`

                _where += conditions

            } else {
                _where += `(${params.where.map(w => `'${w}'`).join(',')})`
            }

            querys.push(_where)
        }

        if ('limit' in params) {
            querys.push('limit=' + params.limit)
        }

        if (querys.length > 0) path += `?${querys.join('&')}`

        return this.request(path);
    }

    async save(model, data) {
        let error = this.validateModel(model);
        if (error) return error;

        error = this.validateData(data);
        if (error) return error;

        return this.request(`${model}/save`, 'POST', data);
    }

    async update(model, data, id) {
        let error = this.validateModel(model);
        if (error) return error;

        error = this.validateData(data);
        if (error) return error;

        if (!id) {
            return {
                error: true,
                message: 'Invalid ID provided for update',
            };
        }

        return this.request(`${model}/update/${id}`, 'PUT', data);
    }

    async unlink(model, id) {
        const error = this.validateModel(model);
        if (error) return error;

        if (!id) {
            return {
                error: true,
                message: 'Invalid ID provided for unlink',
            };
        }

        return this.request(`${model}/unlink/${id}`, 'DELETE');
    }

    setEndpoint(newEndpoint) {
        this.endpoint = newEndpoint;
    }
}
