'use strict';

angular.module('awsCostMonitorApp')
  .filter('reverse', function() {
    return function(items) {
      return items.slice().reverse();
    };
  });

angular.module('awsCostMonitorApp')
  .controller('MainCtrl', function ($scope, $http) {

    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];

    $http.get('/api/all')
      .success(function(instancesList) {
        console.log('Success: ', instancesList);
        $scope.instancesList = instancesList;
      })
      .error(console.log('error retrieving the list'));


  });
