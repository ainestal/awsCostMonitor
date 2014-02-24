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

    $scope.load = function(){
      $scope.loading = true;
      $http.get('/api/all')
        .success(function(response) {
          $scope.instancesList  = response[0];
          $scope.volumesList    = response[1];
          $scope.totalCost      = 0;
          $scope.totalCostDay   = 0;
          $scope.totalCostMonth = 0;
          $scope.totalCostYear  = 0;

          for (var i = 0; i < $scope.instancesList.length; i++){
            if ($scope.instancesList[i]['state'] == 'running'){
              $scope.totalCost      += $scope.instancesList[i]['current_cost'];
              $scope.totalCostDay   += $scope.instancesList[i]['hour_cost'];
              $scope.totalCostMonth += $scope.instancesList[i]['month_cost'];
              $scope.totalCostYear  += $scope.instancesList[i]['year_cost'];              
              $scope.instancesList[i]['aggregated_cost']       = $scope.instancesList[i]['current_cost'];
              $scope.instancesList[i]['aggregated_day_cost']   = $scope.instancesList[i]['day_cost'];
              $scope.instancesList[i]['aggregated_month_cost'] = $scope.instancesList[i]['month_cost'];
              $scope.instancesList[i]['aggregated_year_cost']  = $scope.instancesList[i]['year_cost'];
            }else{
              $scope.instancesList[i]['aggregated_cost']       = 0;
              $scope.instancesList[i]['aggregated_day_cost']   = 0;
              $scope.instancesList[i]['aggregated_month_cost'] = 0;
              $scope.instancesList[i]['aggregated_year_cost']  = 0;            
            }

            $scope.instancesList[i]['volumes'] = [];
            for (var j = 0; j < $scope.volumesList.length; j++){
              if ($scope.instancesList[i]['id'] == $scope.volumesList[j]['instance_id']){              
                $scope.totalCost      += $scope.volumesList[j]['current_cost'];
                $scope.totalCostDay   += $scope.volumesList[j]['day_cost'];
                $scope.totalCostMonth += $scope.volumesList[j]['month_cost'];
                $scope.totalCostYear  += $scope.volumesList[j]['year_cost'];
                $scope.instancesList[i]['aggregated_cost']       += $scope.volumesList[j]['current_cost'];
                $scope.instancesList[i]['aggregated_day_cost']   += $scope.volumesList[j]['day_cost'];
                $scope.instancesList[i]['aggregated_month_cost'] += $scope.volumesList[j]['month_cost'];
                $scope.instancesList[i]['aggregated_year_cost']  += $scope.volumesList[j]['year_cost'];
                $scope.instancesList[i]['volumes'].push($scope.volumesList[j]);
              }
            }
          };
          $scope.loading = false;
        })
        .error(console.log('error retrieving the data'));
      };

    $scope.expandAll = function(){
      for (var i=0; i < $scope.instancesList.length; i++){
        $scope.instancesList[i].isOpen = true;
        $scope.oneAtATime = false;
      };
    };

    $scope.collapseAll = function(){
      for (var i=0; i < $scope.instancesList.length; i++){
        $scope.instancesList[i].isOpen = false;
      };
    };

    $scope.load();
  });
