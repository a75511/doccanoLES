import axios from 'axios'
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

class ApiService {
  constructor() {
    this.instance = axios.create({
      baseURL: process.env.baseUrl
    })
    this.instance.interceptors.request.use((config) => {
      console.log('Request Config:', config);
      return config;
    });

    // Add response interceptor for logging
    this.instance.interceptors.response.use((response) => {
      console.log('Response Data:', response.data);
      return response;
    }, (error) => {
      console.error('Response Error:', error.response?.data || error.message);
      return Promise.reject(error);
    });
  }

  request(method, url, data = {}, config = {}) {
    return this.instance({
      method,
      url,
      data,
      ...config
    })
  }

  get(url, config = {}) {
    return this.request('GET', url, {}, config)
  }

  post(url, data, config = {}) {
    return this.request('POST', url, data, config)
  }

  put(url, data, config = {}) {
    return this.request('PUT', url, data, config)
  }

  patch(url, data, config = {}) {
    return this.request('PATCH', url, data, config)
  }

  delete(url, data = {}, config = {}) {
    return this.request('DELETE', url, data, config)
  }
}

export default new ApiService()
