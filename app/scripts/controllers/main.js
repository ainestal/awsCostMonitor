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
    $scope.totalCost = 0;
    $scope.oneAtATime = true;

    $http.get('/api/all')
      .success(function(response) {
        $scope.instancesList = response[0];
        $scope.volumesList   = response[1];

        var index;
        for (index = 0; index < instancesList.length; ++index) {
          if (instancesList[index].current_cost != 'N/A. Stopped instance'){
            $scope.totalCost = $scope.totalCost + instancesList[index].current_cost;
          }
        }
      })
      .error(console.log('error retrieving the list'));
  });
