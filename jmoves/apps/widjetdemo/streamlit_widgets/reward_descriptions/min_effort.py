import streamlit as st

st.header("Минимальное усилие")

st.markdown(r"""
Транспонированный Якобиан скоростей определяет соотношение между моментами актуаторов и силой приложенной к концевому эффектору в стационарном состоянии:

$$
\tau=J^Tf,
$$

где $\tau$ - моменты актуаторов, $J$ - якобиан связывающий обобщённую скорость $\dot{q}$ и скорость в операционном пространстве $\dot{x}$, $f$ - сила приложенная к концевому эффектору.

Для каждой конфигурации существует наименьшая сила, которую могут создавать двигатели при  "единичном" моменте актуаторов $\|\tau \|=1$. Данная сила пропорциональна обратному значению наибольшего сингулярного числа Якобиана скоростей. Чем большее значение имеет данная характеристика, тем большие внешние силы способен выдерживать механизм. При использовании данного критерия максимизируется минимальное значение допустимой нагрузки. Итоговый критерий равен:

$$
R=\frac{1}{n}\sum_1^n\frac{1}{\sigma_{max}},
$$

где $\sigma_{max}$ - наибольшее сингулярное число Якобиана скоростей, n - число точек на траектории. 
""")