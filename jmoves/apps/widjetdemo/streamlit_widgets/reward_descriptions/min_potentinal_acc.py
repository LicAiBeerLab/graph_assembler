import streamlit as st

st.header("Минимальное потенциальное ускорение")

st.markdown(r"""
Ускорение концевого эффектора зависит от матрицы инерции механизма и моментов актуаторов. Связь моментов актуаторов и ускорения (при нулевой скорости и отбрасывая гравитацию): $$J(q)H(q)^{-1} \tau = \ddot{x} $$где $\tau$ - моменты актуаторов, $J$ - якобиан связывающий обобщённую скорость $\dot{q}$ и скорость в операционном пространстве $\dot{x}$, $\ddot{x}$ - ускорение в операционном пространстве. 

Данный критерий направлен на максимизацию минимального ускорения, получаемого при при  "единичном" моменте актуаторов $\|\tau \|=1$. Значение критерия равно:

$$
R=\frac{1}{n}\sum_1^n\sigma_{min},
$$

где $\sigma_{min}$ - наименьшее сингулярное число матрицы $J(q)H(q)^{-1}$, n - число точек на траектории.
""")