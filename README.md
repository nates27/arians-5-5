# arians-5-5

## Table of contents

* [General info](#general-info)
* [Technologies](#technologies)
* [Aim Of Project](#aim-of-project)
* [Features Explanation](#feature-explanation)
* [Simulation Results](#simulation-results)
* [Conclusion](#conclusion)

## General info

This README contains a brief overview of our team's approach to Huawei Competition

## Technologies

The project is created using:

* Python

## Aim Of Project

The aim of this project is to propose a working solution that can help to model and predict the fluctuations of 500 selected stocks in China to a certain extent by exploring different models and techniques and also have a strategy to optimise revenue in the stock exchange

## Features Explanation

Column name | Description
----------- | -----------
y  | % change in price after 5 mins
x1 | (Current price/price after 5 mins) - 1
x2 | (Current price/price after 10 mins) - 1
x3 | Ratio of buy and sell volume after 5 mins
x4 | Ratio of buy and sell volume after 10 mins

## Simulation Results

Model name | Train RMSE | Test RMSE
----------- | ----------- | ------------
LGBRegressor | 28.20 | 28.13
Linear Regression | 28.53 | 28.30
Ridge Regression | 28.53 | 28.30
Lasso Regression | 28.64 | 28.42
Random Forest Regression | 10.85 | 28.78
XGB Regressor | 27.75 | 28.21
AdaBoost Regression | 32.56 | 32.36

## Conclusion

This project is done to try and see if we can model the patterns of 500 selected stocks in China and to have a strategy to optimise earnings in the stock market and to a certain extent we are able to acheive some results