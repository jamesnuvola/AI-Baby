# Daily variable sweep — 2026-10-28

Generated: 2026-10-28T18:48:54.851920+00:00

**Status:** exploratory. No method is promoted automatically.

Historical segments below were previously explored and are not blind holdouts. Repeated sweeps create multiple-comparison bias.

## superenalotto

Scored targets: 927; history starts 2021-05-13; first target 2022-01-03; latest draw 2026-10-27.

| Method | All mean hits | 2023–24 hits | 2025+ hits | All position exact | All position MAE |
|---|---:|---:|---:|---:|---:|
| anti_hot_window10 | 0.4164 | 0.4385 | 0.4263 | 0.0115 | 38.289 |
| gap_neighbours5 | 0.4347 | 0.4385 | 0.4447 | 0.0236 | 15.714 |
| position_decoder_neighbours20 | 0.4239 | 0.4333 | 0.4342 | 0.0289 | 14.353 |
| gap_neighbours10 | 0.4153 | 0.4333 | 0.4211 | 0.0271 | 14.791 |
| daily_transition_overlap2_power7 | 0.3894 | 0.4282 | 0.3684 | 0.0234 | 15.891 |
| transition_overlap2_power3 | 0.3883 | 0.4205 | 0.3789 | 0.0245 | 15.755 |
| daily_position_decoder_neighbours162 | 0.4045 | 0.4205 | 0.3947 | 0.0284 | 13.968 |
| daily_anti_hot_window120 | 0.4078 | 0.4179 | 0.3789 | 0.0268 | 16.803 |
| global_frequency | 0.3948 | 0.4154 | 0.3816 | 0.0266 | 13.649 |
| position_decoder_neighbours60 | 0.4153 | 0.4154 | 0.4237 | 0.0288 | 14.062 |
| exponential_decay_tau20 | 0.3981 | 0.4128 | 0.3658 | 0.0227 | 15.007 |
| position_decoder_neighbours120 | 0.4067 | 0.4103 | 0.4105 | 0.0284 | 13.967 |
| exponential_decay_tau5 | 0.3959 | 0.4051 | 0.3816 | 0.0261 | 15.025 |
| transition_overlap1_power3 | 0.3786 | 0.4051 | 0.3500 | 0.0205 | 14.921 |
| transition_overlap2_power1 | 0.3873 | 0.4051 | 0.3605 | 0.0225 | 15.638 |
| trajectory_window8_neighbours80 | 0.3991 | 0.4026 | 0.4211 | 0.0324 | 12.743 |
| gap_neighbours40 | 0.4013 | 0.4026 | 0.3921 | 0.0227 | 14.980 |
| daily_gap_neighbours118 | 0.3959 | 0.4026 | 0.3737 | 0.0227 | 15.012 |
| trajectory_window3_neighbours40 | 0.3754 | 0.4000 | 0.3737 | 0.0302 | 12.866 |
| random_uniform_seed0 | 0.4337 | 0.4000 | 0.4447 | 0.0266 | 14.967 |
| transition_overlap2_power2 | 0.3808 | 0.4000 | 0.3684 | 0.0212 | 15.626 |
| transition_overlap1_power1 | 0.3722 | 0.3949 | 0.3211 | 0.0252 | 14.326 |
| transition_overlap1_power2 | 0.3765 | 0.3949 | 0.3342 | 0.0237 | 14.545 |
| recent_frequency_window10 | 0.3937 | 0.3923 | 0.3737 | 0.0200 | 19.867 |
| exponential_decay_tau40 | 0.3959 | 0.3923 | 0.3921 | 0.0239 | 14.697 |
| transition_overlap3_power1 | 0.3873 | 0.3923 | 0.3789 | 0.0216 | 18.109 |
| transition_overlap3_power2 | 0.3883 | 0.3923 | 0.3816 | 0.0218 | 18.106 |
| transition_overlap3_power3 | 0.3883 | 0.3923 | 0.3816 | 0.0219 | 18.099 |
| daily_exponential_decay_tau118 | 0.3765 | 0.3897 | 0.3553 | 0.0223 | 14.509 |
| recent_frequency_window80 | 0.3894 | 0.3872 | 0.3711 | 0.0241 | 15.262 |
| exponential_decay_tau10 | 0.3981 | 0.3872 | 0.3737 | 0.0236 | 14.942 |
| gap_neighbours20 | 0.4067 | 0.3872 | 0.3947 | 0.0252 | 15.017 |
| daily_recent_window218 | 0.3657 | 0.3872 | 0.3447 | 0.0212 | 15.642 |
| daily_trajectory_window6_neighbours36 | 0.3808 | 0.3718 | 0.4079 | 0.0289 | 12.940 |
| recent_frequency_window20 | 0.3937 | 0.3667 | 0.4158 | 0.0212 | 17.695 |
| trajectory_window5_neighbours60 | 0.3819 | 0.3615 | 0.4105 | 0.0302 | 12.737 |
| overdue_first | 0.3851 | 0.3615 | 0.3947 | 0.0223 | 15.903 |
| anti_hot_window20 | 0.3830 | 0.3590 | 0.4184 | 0.0138 | 31.872 |
| recent_frequency_window40 | 0.3668 | 0.3436 | 0.3816 | 0.0203 | 16.053 |
| anti_hot_window40 | 0.3700 | 0.3103 | 0.3842 | 0.0210 | 18.175 |

## vincicasa

Scored targets: 1761; history starts 2021-09-23; first target 2022-01-01; latest draw 2026-10-27.

| Method | All mean hits | 2023–24 hits | 2025+ hits | All position exact | All position MAE |
|---|---:|---:|---:|---:|---:|
| overdue_first | 0.6349 | 0.6689 | 0.6075 | 0.0584 | 6.844 |
| gap_neighbours5 | 0.6616 | 0.6607 | 0.6827 | 0.0564 | 7.090 |
| transition_overlap2_power3 | 0.6553 | 0.6594 | 0.6406 | 0.0560 | 6.907 |
| random_uniform_seed0 | 0.6337 | 0.6539 | 0.6331 | 0.0562 | 6.848 |
| daily_transition_overlap2_power7 | 0.6502 | 0.6525 | 0.6481 | 0.0558 | 6.894 |
| transition_overlap2_power2 | 0.6468 | 0.6512 | 0.6331 | 0.0560 | 6.864 |
| trajectory_window8_neighbours80 | 0.6303 | 0.6443 | 0.6301 | 0.0747 | 5.865 |
| transition_overlap1_power3 | 0.6468 | 0.6443 | 0.6466 | 0.0559 | 6.894 |
| position_decoder_neighbours120 | 0.6564 | 0.6430 | 0.6662 | 0.0713 | 6.093 |
| daily_position_decoder_neighbours162 | 0.6542 | 0.6430 | 0.6632 | 0.0716 | 6.069 |
| transition_overlap3_power1 | 0.6354 | 0.6402 | 0.6331 | 0.0478 | 7.918 |
| position_decoder_neighbours20 | 0.6519 | 0.6389 | 0.6617 | 0.0672 | 6.351 |
| transition_overlap3_power2 | 0.6354 | 0.6389 | 0.6346 | 0.0479 | 7.916 |
| daily_anti_hot_window120 | 0.6383 | 0.6389 | 0.6421 | 0.0561 | 7.172 |
| transition_overlap3_power3 | 0.6388 | 0.6375 | 0.6466 | 0.0493 | 7.857 |
| daily_recent_window218 | 0.6422 | 0.6375 | 0.6647 | 0.0563 | 6.933 |
| transition_overlap2_power1 | 0.6332 | 0.6361 | 0.6195 | 0.0555 | 6.938 |
| trajectory_window5_neighbours60 | 0.6235 | 0.6347 | 0.6075 | 0.0711 | 5.913 |
| anti_hot_window20 | 0.6207 | 0.6347 | 0.6105 | 0.0484 | 8.291 |
| gap_neighbours40 | 0.6377 | 0.6306 | 0.6617 | 0.0542 | 6.886 |
| position_decoder_neighbours60 | 0.6468 | 0.6252 | 0.6586 | 0.0693 | 6.217 |
| anti_hot_window40 | 0.6258 | 0.6252 | 0.6105 | 0.0482 | 7.628 |
| daily_exponential_decay_tau118 | 0.6371 | 0.6238 | 0.6692 | 0.0576 | 6.828 |
| transition_overlap1_power2 | 0.6383 | 0.6224 | 0.6406 | 0.0541 | 6.889 |
| daily_trajectory_window6_neighbours36 | 0.6190 | 0.6211 | 0.6045 | 0.0683 | 6.000 |
| trajectory_window3_neighbours40 | 0.6303 | 0.6183 | 0.6316 | 0.0689 | 5.869 |
| anti_hot_window10 | 0.6195 | 0.6183 | 0.6301 | 0.0368 | 10.905 |
| gap_neighbours10 | 0.6474 | 0.6129 | 0.6812 | 0.0580 | 6.876 |
| recent_frequency_window80 | 0.6326 | 0.6088 | 0.6842 | 0.0546 | 7.163 |
| transition_overlap1_power1 | 0.6337 | 0.6074 | 0.6677 | 0.0587 | 6.970 |
| gap_neighbours20 | 0.6337 | 0.5923 | 0.6662 | 0.0572 | 6.929 |
| recent_frequency_window10 | 0.5928 | 0.5910 | 0.6015 | 0.0445 | 7.722 |
| recent_frequency_window20 | 0.6053 | 0.5896 | 0.6301 | 0.0500 | 7.385 |
| exponential_decay_tau10 | 0.6133 | 0.5896 | 0.6361 | 0.0526 | 7.062 |
| recent_frequency_window40 | 0.6070 | 0.5841 | 0.6391 | 0.0520 | 7.244 |
| exponential_decay_tau40 | 0.6167 | 0.5800 | 0.6481 | 0.0519 | 7.103 |
| daily_gap_neighbours118 | 0.6195 | 0.5800 | 0.6586 | 0.0529 | 6.929 |
| exponential_decay_tau5 | 0.5928 | 0.5691 | 0.6015 | 0.0493 | 7.093 |
| global_frequency | 0.6144 | 0.5677 | 0.6632 | 0.0587 | 6.758 |
| exponential_decay_tau20 | 0.6031 | 0.5636 | 0.6481 | 0.0507 | 7.053 |

