; UTF-8 multi-form demonstration
(define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1))))))
(define make-adder (lambda (x) (lambda (y) (+ x y))))
(define add10 (make-adder 10))
(display "計算結果: ")
(display (list (fact 5) (add10 3)))
(newline)
(list (fact 5) (add10 3))
