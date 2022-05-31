#pragma once

#include <vector>
#include <string>
#include <iostream>
#include "v2/Api.hpp"

// Api
typedef api::v2::DataObject DataObject;
typedef api::v2::Application Application;
typedef api::v2::Api Api;
using api::Value;

// provides an API instance
class ApiFixture
{
public:
  ApiFixture();
  ~ApiFixture();

  static Api* GetInstance() {return instance;}
private:
  ApiFixture(const ApiFixture&) {};
  static Api* instance;
};


//resource guard that ensures that value pointers are released
class ValueGuard
{
public:
  ValueGuard(const api::Value* val) : m_val(val){};
  ~ValueGuard();

  const api::Value* operator->() const  { return m_val; }

private:
  ValueGuard() {};
  ValueGuard(const ValueGuard&) {};
  const api::Value* m_val;
};


//some utility functions
class Utils
{
public:
  static std::vector<DataObject*> GetChildren(DataObject* parent, std::string classNameFilter);
};
