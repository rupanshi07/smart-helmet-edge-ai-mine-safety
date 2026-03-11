// ============================================================
//  AUTO-GENERATED — Smart Helmet Mine Safety
//  Decision Tree Model — ESP32 WROOM
//
//  Generated from : D:\IoT_Project\smart_helmet_mine_dataset.csv
//  Train accuracy : 96.80%
//  Test  accuracy : 93.18%
//  Tree depth     : 11
//  Tree nodes     : 233
//
//  Place in: D:\IoT_Project\Arduino\smart_helmet_dt\
//  features[] array order (MUST match exactly):
//    features[ 0] = temperature_C
//    features[ 1] = humidity_pct
//    features[ 2] = gas_ppm
//    features[ 3] = acc_x_g
//    features[ 4] = acc_y_g
//    features[ 5] = acc_z_g
//    features[ 6] = acc_resultant_g
//    features[ 7] = gyro_x_dps
//    features[ 8] = gyro_y_dps
//    features[ 9] = gyro_z_dps
//    features[10] = gyro_resultant_dps
//
//  NO normalization needed — raw sensor values go straight in!
//  NO TFLite library needed — pure C if/else logic
// ============================================================

#ifndef DECISION_TREE_MODEL_H
#define DECISION_TREE_MODEL_H

#define NUM_FEATURES  11
#define NUM_CLASSES   3

// Class index → label
// 0 = EMERGENCY
// 1 = NORMAL
// 2 = WARNING
const char* CLASS_LABELS[NUM_CLASSES] = { "EMERGENCY", "NORMAL", "WARNING" };

const char* FEATURE_NAMES[NUM_FEATURES] = { "temperature_C", "humidity_pct", "gas_ppm", "acc_x_g", "acc_y_g", "acc_z_g", "acc_resultant_g", "gyro_x_dps", "gyro_y_dps", "gyro_z_dps", "gyro_resultant_dps" };

// Safety thresholds — mine environment
#define TEMP_WARNING_THRESH    35.0f
#define TEMP_EMERGENCY_THRESH  50.0f
#define GAS_WARNING_THRESH     1000.0f
#define GAS_EMERGENCY_THRESH   3000.0f
#define ACC_WARNING_THRESH     2.0f
#define ACC_EMERGENCY_THRESH   4.0f
#define GYRO_WARNING_THRESH    60.0f
#define GYRO_EMERGENCY_THRESH  200.0f

int predict(float features[NUM_FEATURES]) {
if (features[2] <= 1300.099976f) {  // gas_ppm <= 1300.1000
  if (features[0] <= 36.500000f) {  // temperature_C <= 36.5000
    if (features[6] <= 3.281850f) {  // acc_resultant_g <= 3.2818
      if (features[0] <= 35.500000f) {  // temperature_C <= 35.5000
        if (features[4] <= -2.125350f) {  // acc_y_g <= -2.1253
          return 1;  // NORMAL (samples=9, confidence=0.00)
        } else {  // acc_y_g > -2.1253
          if (features[1] <= 91.500000f) {  // humidity_pct <= 91.5000
            if (features[5] <= -2.330600f) {  // acc_z_g <= -2.3306
              return 1;  // NORMAL (samples=5, confidence=0.20)
            } else {  // acc_z_g > -2.3306
              return 1;  // NORMAL (samples=2132, confidence=0.00)
            }
          } else {  // humidity_pct > 91.5000
            if (features[5] <= -1.467150f) {  // acc_z_g <= -1.4672
              return 1;  // NORMAL (samples=5, confidence=0.00)
            } else {  // acc_z_g > -1.4672
              return 1;  // NORMAL (samples=16, confidence=0.06)
            }
          }
        }
      } else {  // temperature_C > 35.5000
        if (features[7] <= 30.307500f) {  // gyro_x_dps <= 30.3075
          if (features[3] <= 0.399900f) {  // acc_x_g <= 0.3999
            return 1;  // NORMAL (samples=20, confidence=0.05)
          } else {  // acc_x_g > 0.3999
            if (features[6] <= 1.457800f) {  // acc_resultant_g <= 1.4578
              return 2;  // WARNING (samples=5, confidence=0.00)
            } else {  // acc_resultant_g > 1.4578
              return 1;  // NORMAL (samples=5, confidence=0.20)
            }
          }
        } else {  // gyro_x_dps > 30.3075
          return 2;  // WARNING (samples=5, confidence=0.00)
        }
      }
    } else {  // acc_resultant_g > 3.2818
      if (features[8] <= -45.344999f) {  // gyro_y_dps <= -45.3450
        if (features[1] <= 90.000000f) {  // humidity_pct <= 90.0000
          return 2;  // WARNING (samples=5, confidence=0.00)
        } else {  // humidity_pct > 90.0000
          return 2;  // WARNING (samples=9, confidence=0.11)
        }
      } else {  // gyro_y_dps > -45.3450
        if (features[0] <= 31.500000f) {  // temperature_C <= 31.5000
          if (features[9] <= -70.098000f) {  // gyro_z_dps <= -70.0980
            return 1;  // NORMAL (samples=5, confidence=0.00)
          } else {  // gyro_z_dps > -70.0980
            return 1;  // NORMAL (samples=7, confidence=0.14)
          }
        } else {  // temperature_C > 31.5000
          if (features[8] <= 35.360500f) {  // gyro_y_dps <= 35.3605
            return 1;  // NORMAL (samples=7, confidence=0.00)
          } else {  // gyro_y_dps > 35.3605
            return 2;  // WARNING (samples=6, confidence=0.17)
          }
        }
      }
    }
  } else {  // temperature_C > 36.5000
    if (features[0] <= 38.500000f) {  // temperature_C <= 38.5000
      if (features[6] <= 2.482000f) {  // acc_resultant_g <= 2.4820
        if (features[2] <= 1045.399963f) {  // gas_ppm <= 1045.4000
          if (features[10] <= 39.463999f) {  // gyro_resultant_dps <= 39.4640
            return 1;  // NORMAL (samples=14, confidence=0.07)
          } else {  // gyro_resultant_dps > 39.4640
            return 1;  // NORMAL (samples=5, confidence=0.00)
          }
        } else {  // gas_ppm > 1045.4000
          if (features[1] <= 86.000000f) {  // humidity_pct <= 86.0000
            return 1;  // NORMAL (samples=7, confidence=0.14)
          } else {  // humidity_pct > 86.0000
            if (features[3] <= -0.616700f) {  // acc_x_g <= -0.6167
              return 2;  // WARNING (samples=5, confidence=0.00)
            } else {  // acc_x_g > -0.6167
              return 2;  // WARNING (samples=6, confidence=0.00)
            }
          }
        }
      } else {  // acc_resultant_g > 2.4820
        if (features[4] <= 0.682050f) {  // acc_y_g <= 0.6821
          return 2;  // WARNING (samples=5, confidence=0.20)
        } else {  // acc_y_g > 0.6821
          return 2;  // WARNING (samples=7, confidence=0.14)
        }
      }
    } else {  // temperature_C > 38.5000
      if (features[2] <= 963.549988f) {  // gas_ppm <= 963.5500
        if (features[6] <= 1.901400f) {  // acc_resultant_g <= 1.9014
          if (features[0] <= 42.500000f) {  // temperature_C <= 42.5000
            if (features[8] <= 3.885500f) {  // gyro_y_dps <= 3.8855
              if (features[3] <= -0.093550f) {  // acc_x_g <= -0.0936
                return 2;  // WARNING (samples=6, confidence=0.00)
              } else {  // acc_x_g > -0.0936
                return 1;  // NORMAL (samples=7, confidence=0.00)
              }
            } else {  // gyro_y_dps > 3.8855
              return 1;  // NORMAL (samples=6, confidence=0.17)
            }
          } else {  // temperature_C > 42.5000
            if (features[0] <= 44.500000f) {  // temperature_C <= 44.5000
              return 2;  // WARNING (samples=5, confidence=0.00)
            } else {  // temperature_C > 44.5000
              return 2;  // WARNING (samples=10, confidence=0.10)
            }
          }
        } else {  // acc_resultant_g > 1.9014
          if (features[0] <= 39.500000f) {  // temperature_C <= 39.5000
            return 2;  // WARNING (samples=7, confidence=0.00)
          } else {  // temperature_C > 39.5000
            return 2;  // WARNING (samples=18, confidence=0.06)
          }
        }
      } else {  // gas_ppm > 963.5500
        if (features[0] <= 39.500000f) {  // temperature_C <= 39.5000
          if (features[2] <= 1112.150024f) {  // gas_ppm <= 1112.1500
            return 2;  // WARNING (samples=7, confidence=0.00)
          } else {  // gas_ppm > 1112.1500
            return 2;  // WARNING (samples=12, confidence=0.08)
          }
        } else {  // temperature_C > 39.5000
          return 2;  // WARNING (samples=81, confidence=0.01)
        }
      }
    }
  }
} else {  // gas_ppm > 1300.1000
  if (features[0] <= 43.500000f) {  // temperature_C <= 43.5000
    if (features[2] <= 2900.900024f) {  // gas_ppm <= 2900.9000
      if (features[0] <= 30.500000f) {  // temperature_C <= 30.5000
        if (features[6] <= 1.776900f) {  // acc_resultant_g <= 1.7769
          if (features[2] <= 2778.050049f) {  // gas_ppm <= 2778.0500
            if (features[8] <= -12.940500f) {  // gyro_y_dps <= -12.9405
              return 2;  // WARNING (samples=8, confidence=0.00)
            } else {  // gyro_y_dps > -12.9405
              if (features[1] <= 90.500000f) {  // humidity_pct <= 90.5000
                if (features[2] <= 2613.900024f) {  // gas_ppm <= 2613.9000
                  return 1;  // NORMAL (samples=180, confidence=0.01)
                } else {  // gas_ppm > 2613.9000
                  if (features[2] <= 2649.650024f) {  // gas_ppm <= 2649.6500
                    return 2;  // WARNING (samples=5, confidence=0.00)
                  } else {  // gas_ppm > 2649.6500
                    return 1;  // NORMAL (samples=8, confidence=0.12)
                  }
                }
              } else {  // humidity_pct > 90.5000
                return 2;  // WARNING (samples=5, confidence=0.00)
              }
            }
          } else {  // gas_ppm > 2778.0500
            if (features[2] <= 2856.550049f) {  // gas_ppm <= 2856.5500
              return 2;  // WARNING (samples=5, confidence=0.00)
            } else {  // gas_ppm > 2856.5500
              return 2;  // WARNING (samples=5, confidence=0.20)
            }
          }
        } else {  // acc_resultant_g > 1.7769
          if (features[10] <= 182.147499f) {  // gyro_resultant_dps <= 182.1475
            if (features[2] <= 1614.600037f) {  // gas_ppm <= 1614.6000
              if (features[8] <= 18.534500f) {  // gyro_y_dps <= 18.5345
                return 1;  // NORMAL (samples=12, confidence=0.08)
              } else {  // gyro_y_dps > 18.5345
                return 2;  // WARNING (samples=5, confidence=0.00)
              }
            } else {  // gas_ppm > 1614.6000
              if (features[9] <= 14.828500f) {  // gyro_z_dps <= 14.8285
                if (features[1] <= 80.000000f) {  // humidity_pct <= 80.0000
                  return 1;  // NORMAL (samples=5, confidence=0.00)
                } else {  // humidity_pct > 80.0000
                  if (features[9] <= -9.550500f) {  // gyro_z_dps <= -9.5505
                    if (features[8] <= -6.326500f) {  // gyro_y_dps <= -6.3265
                      return 2;  // WARNING (samples=5, confidence=0.00)
                    } else {  // gyro_y_dps > -6.3265
                      return 2;  // WARNING (samples=6, confidence=0.17)
                    }
                  } else {  // gyro_z_dps > -9.5505
                    return 2;  // WARNING (samples=6, confidence=0.00)
                  }
                }
              } else {  // gyro_z_dps > 14.8285
                return 1;  // NORMAL (samples=5, confidence=0.20)
              }
            }
          } else {  // gyro_resultant_dps > 182.1475
            if (features[3] <= -2.178000f) {  // acc_x_g <= -2.1780
              return 2;  // WARNING (samples=5, confidence=0.20)
            } else {  // acc_x_g > -2.1780
              return 2;  // WARNING (samples=24, confidence=0.04)
            }
          }
        }
      } else {  // temperature_C > 30.5000
        if (features[6] <= 3.395200f) {  // acc_resultant_g <= 3.3952
          if (features[0] <= 33.500000f) {  // temperature_C <= 33.5000
            if (features[2] <= 1899.150024f) {  // gas_ppm <= 1899.1500
              if (features[6] <= 2.542700f) {  // acc_resultant_g <= 2.5427
                if (features[2] <= 1632.649963f) {  // gas_ppm <= 1632.6500
                  return 1;  // NORMAL (samples=44, confidence=0.02)
                } else {  // gas_ppm > 1632.6500
                  if (features[1] <= 84.500000f) {  // humidity_pct <= 84.5000
                    if (features[9] <= -10.160000f) {  // gyro_z_dps <= -10.1600
                      return 1;  // NORMAL (samples=5, confidence=0.00)
                    } else {  // gyro_z_dps > -10.1600
                      return 1;  // NORMAL (samples=15, confidence=0.07)
                    }
                  } else {  // humidity_pct > 84.5000
                    if (features[6] <= 1.638000f) {  // acc_resultant_g <= 1.6380
                      return 2;  // WARNING (samples=8, confidence=0.00)
                    } else {  // acc_resultant_g > 1.6380
                      return 1;  // NORMAL (samples=5, confidence=0.20)
                    }
                  }
                }
              } else {  // acc_resultant_g > 2.5427
                if (features[2] <= 1574.299988f) {  // gas_ppm <= 1574.3000
                  return 2;  // WARNING (samples=6, confidence=0.00)
                } else {  // gas_ppm > 1574.3000
                  return 2;  // WARNING (samples=8, confidence=0.12)
                }
              }
            } else {  // gas_ppm > 1899.1500
              if (features[2] <= 2240.349976f) {  // gas_ppm <= 2240.3500
                if (features[1] <= 84.500000f) {  // humidity_pct <= 84.5000
                  return 2;  // WARNING (samples=9, confidence=0.00)
                } else {  // humidity_pct > 84.5000
                  if (features[4] <= -0.160600f) {  // acc_y_g <= -0.1606
                    return 2;  // WARNING (samples=12, confidence=0.08)
                  } else {  // acc_y_g > -0.1606
                    return 2;  // WARNING (samples=9, confidence=0.00)
                  }
                }
              } else {  // gas_ppm > 2240.3500
                if (features[7] <= -13.026500f) {  // gyro_x_dps <= -13.0265
                  if (features[2] <= 2527.449951f) {  // gas_ppm <= 2527.4500
                    return 2;  // WARNING (samples=5, confidence=0.00)
                  } else {  // gas_ppm > 2527.4500
                    return 2;  // WARNING (samples=5, confidence=0.20)
                  }
                } else {  // gyro_x_dps > -13.0265
                  if (features[2] <= 2308.799927f) {  // gas_ppm <= 2308.7999
                    return 2;  // WARNING (samples=5, confidence=0.20)
                  } else {  // gas_ppm > 2308.7999
                    return 2;  // WARNING (samples=25, confidence=0.04)
                  }
                }
              }
            }
          } else {  // temperature_C > 33.5000
            if (features[2] <= 2409.750000f) {  // gas_ppm <= 2409.7500
              if (features[10] <= 163.190002f) {  // gyro_resultant_dps <= 163.1900
                if (features[1] <= 77.500000f) {  // humidity_pct <= 77.5000
                  if (features[10] <= 37.460501f) {  // gyro_resultant_dps <= 37.4605
                    return 1;  // NORMAL (samples=6, confidence=0.00)
                  } else {  // gyro_resultant_dps > 37.4605
                    return 2;  // WARNING (samples=7, confidence=0.00)
                  }
                } else {  // humidity_pct > 77.5000
                  if (features[2] <= 1362.200012f) {  // gas_ppm <= 1362.2000
                    if (features[0] <= 35.500000f) {  // temperature_C <= 35.5000
                      return 1;  // NORMAL (samples=7, confidence=0.14)
                    } else {  // temperature_C > 35.5000
                      return 2;  // WARNING (samples=22, confidence=0.00)
                    }
                  } else {  // gas_ppm > 1362.2000
                    if (features[0] <= 42.500000f) {  // temperature_C <= 42.5000
                      return 2;  // WARNING (samples=440, confidence=0.00)
                    } else {  // temperature_C > 42.5000
                      return 2;  // WARNING (samples=44, confidence=0.00)
                    }
                  }
                }
              } else {  // gyro_resultant_dps > 163.1900
                if (features[4] <= -1.066150f) {  // acc_y_g <= -1.0661
                  return 0;  // EMERGENCY (samples=5, confidence=0.00)
                } else {  // acc_y_g > -1.0661
                  return 2;  // WARNING (samples=5, confidence=0.20)
                }
              }
            } else {  // gas_ppm > 2409.7500
              if (features[0] <= 41.500000f) {  // temperature_C <= 41.5000
                if (features[6] <= 1.879000f) {  // acc_resultant_g <= 1.8790
                  if (features[9] <= 4.343500f) {  // gyro_z_dps <= 4.3435
                    return 2;  // WARNING (samples=44, confidence=0.02)
                  } else {  // gyro_z_dps > 4.3435
                    if (features[9] <= 6.507500f) {  // gyro_z_dps <= 6.5075
                      return 0;  // EMERGENCY (samples=5, confidence=0.00)
                    } else {  // gyro_z_dps > 6.5075
                      return 2;  // WARNING (samples=7, confidence=0.14)
                    }
                  }
                } else {  // acc_resultant_g > 1.8790
                  return 0;  // EMERGENCY (samples=9, confidence=0.00)
                }
              } else {  // temperature_C > 41.5000
                if (features[1] <= 87.500000f) {  // humidity_pct <= 87.5000
                  return 0;  // EMERGENCY (samples=7, confidence=0.00)
                } else {  // humidity_pct > 87.5000
                  return 0;  // EMERGENCY (samples=8, confidence=0.00)
                }
              }
            }
          }
        } else {  // acc_resultant_g > 3.3952
          if (features[0] <= 37.500000f) {  // temperature_C <= 37.5000
            if (features[1] <= 88.500000f) {  // humidity_pct <= 88.5000
              if (features[2] <= 1699.049988f) {  // gas_ppm <= 1699.0500
                return 2;  // WARNING (samples=5, confidence=0.20)
              } else {  // gas_ppm > 1699.0500
                return 2;  // WARNING (samples=17, confidence=0.06)
              }
            } else {  // humidity_pct > 88.5000
              if (features[2] <= 2017.650024f) {  // gas_ppm <= 2017.6500
                return 2;  // WARNING (samples=8, confidence=0.12)
              } else {  // gas_ppm > 2017.6500
                return 0;  // EMERGENCY (samples=9, confidence=0.00)
              }
            }
          } else {  // temperature_C > 37.5000
            if (features[2] <= 2177.250000f) {  // gas_ppm <= 2177.2500
              if (features[1] <= 90.500000f) {  // humidity_pct <= 90.5000
                return 0;  // EMERGENCY (samples=9, confidence=0.00)
              } else {  // humidity_pct > 90.5000
                return 2;  // WARNING (samples=6, confidence=0.17)
              }
            } else {  // gas_ppm > 2177.2500
              return 0;  // EMERGENCY (samples=14, confidence=0.07)
            }
          }
        }
      }
    } else {  // gas_ppm > 2900.9000
      if (features[0] <= 34.500000f) {  // temperature_C <= 34.5000
        if (features[0] <= 31.500000f) {  // temperature_C <= 31.5000
          if (features[2] <= 3846.849976f) {  // gas_ppm <= 3846.8500
            if (features[2] <= 3107.600098f) {  // gas_ppm <= 3107.6001
              if (features[10] <= 61.622999f) {  // gyro_resultant_dps <= 61.6230
                return 2;  // WARNING (samples=9, confidence=0.00)
              } else {  // gyro_resultant_dps > 61.6230
                return 2;  // WARNING (samples=15, confidence=0.07)
              }
            } else {  // gas_ppm > 3107.6001
              return 2;  // WARNING (samples=66, confidence=0.02)
            }
          } else {  // gas_ppm > 3846.8500
            if (features[0] <= 30.500000f) {  // temperature_C <= 30.5000
              if (features[7] <= 159.871994f) {  // gyro_x_dps <= 159.8720
                if (features[3] <= -1.624600f) {  // acc_x_g <= -1.6246
                  return 2;  // WARNING (samples=5, confidence=0.20)
                } else {  // acc_x_g > -1.6246
                  return 2;  // WARNING (samples=24, confidence=0.04)
                }
              } else {  // gyro_x_dps > 159.8720
                return 2;  // WARNING (samples=5, confidence=0.00)
              }
            } else {  // temperature_C > 30.5000
              return 0;  // EMERGENCY (samples=7, confidence=0.00)
            }
          }
        } else {  // temperature_C > 31.5000
          if (features[2] <= 3844.449951f) {  // gas_ppm <= 3844.4500
            if (features[6] <= 4.906350f) {  // acc_resultant_g <= 4.9063
              if (features[8] <= 39.811501f) {  // gyro_y_dps <= 39.8115
                if (features[1] <= 82.500000f) {  // humidity_pct <= 82.5000
                  return 2;  // WARNING (samples=6, confidence=0.17)
                } else {  // humidity_pct > 82.5000
                  return 2;  // WARNING (samples=21, confidence=0.05)
                }
              } else {  // gyro_y_dps > 39.8115
                return 0;  // EMERGENCY (samples=5, confidence=0.00)
              }
            } else {  // acc_resultant_g > 4.9063
              return 0;  // EMERGENCY (samples=8, confidence=0.00)
            }
          } else {  // gas_ppm > 3844.4500
            return 0;  // EMERGENCY (samples=9, confidence=0.00)
          }
        }
      } else {  // temperature_C > 34.5000
        if (features[10] <= 55.679001f) {  // gyro_resultant_dps <= 55.6790
          if (features[0] <= 36.500000f) {  // temperature_C <= 36.5000
            return 2;  // WARNING (samples=9, confidence=0.11)
          } else {  // temperature_C > 36.5000
            if (features[1] <= 83.500000f) {  // humidity_pct <= 83.5000
              return 2;  // WARNING (samples=6, confidence=0.00)
            } else {  // humidity_pct > 83.5000
              if (features[3] <= 0.087700f) {  // acc_x_g <= 0.0877
                return 0;  // EMERGENCY (samples=18, confidence=0.06)
              } else {  // acc_x_g > 0.0877
                return 0;  // EMERGENCY (samples=8, confidence=0.00)
              }
            }
          }
        } else {  // gyro_resultant_dps > 55.6790
          if (features[0] <= 35.500000f) {  // temperature_C <= 35.5000
            if (features[8] <= 53.185501f) {  // gyro_y_dps <= 53.1855
              return 0;  // EMERGENCY (samples=10, confidence=0.10)
            } else {  // gyro_y_dps > 53.1855
              return 0;  // EMERGENCY (samples=6, confidence=0.00)
            }
          } else {  // temperature_C > 35.5000
            if (features[6] <= 2.021350f) {  // acc_resultant_g <= 2.0214
              return 0;  // EMERGENCY (samples=5, confidence=0.00)
            } else {  // acc_resultant_g > 2.0214
              return 0;  // EMERGENCY (samples=70, confidence=0.01)
            }
          }
        }
      }
    }
  } else {  // temperature_C > 43.5000
    if (features[2] <= 1930.299988f) {  // gas_ppm <= 1930.3000
      if (features[8] <= 8.457000f) {  // gyro_y_dps <= 8.4570
        if (features[2] <= 1560.549988f) {  // gas_ppm <= 1560.5500
          return 2;  // WARNING (samples=16, confidence=0.06)
        } else {  // gas_ppm > 1560.5500
          if (features[4] <= 0.316550f) {  // acc_y_g <= 0.3166
            if (features[2] <= 1762.650024f) {  // gas_ppm <= 1762.6500
              if (features[9] <= -7.751500f) {  // gyro_z_dps <= -7.7515
                return 0;  // EMERGENCY (samples=5, confidence=0.00)
              } else {  // gyro_z_dps > -7.7515
                return 2;  // WARNING (samples=5, confidence=0.00)
              }
            } else {  // gas_ppm > 1762.6500
              return 2;  // WARNING (samples=9, confidence=0.11)
            }
          } else {  // acc_y_g > 0.3166
            return 0;  // EMERGENCY (samples=7, confidence=0.00)
          }
        }
      } else {  // gyro_y_dps > 8.4570
        if (features[0] <= 45.500000f) {  // temperature_C <= 45.5000
          return 2;  // WARNING (samples=7, confidence=0.00)
        } else {  // temperature_C > 45.5000
          if (features[1] <= 86.500000f) {  // humidity_pct <= 86.5000
            return 0;  // EMERGENCY (samples=7, confidence=0.00)
          } else {  // humidity_pct > 86.5000
            return 0;  // EMERGENCY (samples=7, confidence=0.14)
          }
        }
      }
    } else {  // gas_ppm > 1930.3000
      if (features[2] <= 2407.099976f) {  // gas_ppm <= 2407.1000
        if (features[0] <= 44.500000f) {  // temperature_C <= 44.5000
          if (features[1] <= 90.500000f) {  // humidity_pct <= 90.5000
            return 2;  // WARNING (samples=7, confidence=0.00)
          } else {  // humidity_pct > 90.5000
            return 0;  // EMERGENCY (samples=6, confidence=0.17)
          }
        } else {  // temperature_C > 44.5000
          if (features[2] <= 1974.399963f) {  // gas_ppm <= 1974.4000
            return 0;  // EMERGENCY (samples=5, confidence=0.00)
          } else {  // gas_ppm > 1974.4000
            if (features[6] <= 1.141150f) {  // acc_resultant_g <= 1.1411
              return 0;  // EMERGENCY (samples=5, confidence=0.20)
            } else {  // acc_resultant_g > 1.1411
              return 0;  // EMERGENCY (samples=22, confidence=0.05)
            }
          }
        }
      } else {  // gas_ppm > 2407.1000
        return 0;  // EMERGENCY (samples=397, confidence=0.00)
      }
    }
  }
}
}

int safety_override(float features[NUM_FEATURES], int prediction) {
  bool hard_emergency = (features[0] >= TEMP_EMERGENCY_THRESH) ||
                        (features[2] >= GAS_EMERGENCY_THRESH)  ||
                        (features[6] >= ACC_EMERGENCY_THRESH && features[10] >= GYRO_EMERGENCY_THRESH);
  if (hard_emergency) return 0;

  bool hard_warning = (features[0] >= TEMP_WARNING_THRESH) ||
                      (features[2] >= GAS_WARNING_THRESH)  ||
                      (features[6] >= ACC_WARNING_THRESH);
  if (hard_warning && prediction == 1) return 2;

  return prediction;
}

#endif // DECISION_TREE_MODEL_H