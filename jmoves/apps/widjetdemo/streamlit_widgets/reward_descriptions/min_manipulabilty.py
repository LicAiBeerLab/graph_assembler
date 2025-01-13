import streamlit as st

st.header("Минимальная манипулируемость")

st.markdown(r"""
Манипулируемость это кинематическая характеристика оценивающая связь между скоростью актуаторов и скоростью концевого эффектора. Данный критерий зависит от минимального значения скорости концевого эффектора при "единичной" скорости актуаторов $\|q\|=1$. Наименьшее значение определяется наименьшим сингулярным числом Якобиана скоростей. Значение критерия равно:

$$
R=\frac{1}{n}\sum_1^n\sigma_{min},
$$
где $\sigma_{min}$ - наименьшее сингулярное число Якобиана скоростей, n - число точек на траектории.

---
            
1. M. Švejda, "New kinetostatic criterion for robot parametric optimization," _2017 IEEE 4th International Conference on Soft Computing & Machine Intelligence (ISCMI)_, Mauritius, 2017, pp. 66-70, doi: [10.1109/ISCMI.2017.8279599](https://doi.org/10.1109/ISCMI.2017.8279599
""")
