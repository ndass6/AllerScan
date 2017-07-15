import axios from 'axios';

var api = {
  getData: function() {
    return axios.get('/api')
      .then(function (data) {
        return data.data;
      })
      .catch(function (err) { console.warn('Error in getData', err) })
  }
};

export {api};
