; Lisp-written REPL. Host read/read-line/guard are explicit service boundaries.
; Iteration uses host Lisp's while special form, avoiding Python recursion per line.
(define m-repl
  (lambda (env)
    (begin
      (define done #f)
      (while (not done)
        (begin
          (define line (read-line))
          (if (if (equal? line #f) #t (equal? line ":quit"))
            (set! done #t)
            (if (equal? line "") '()
              (begin
                ; Keep evaluation AND printing inside guard: a huge integer
                ; may evaluate successfully but exceed host decimal print limits.
                (define outcome
                  (guard (lambda ()
                    (display (m-sequence (read-all line) env 0))
                    (newline)
                    #t)))
                (if (car outcome) '()
                  (begin (display "error: ") (display (m-second outcome)) (newline)))))))))))
