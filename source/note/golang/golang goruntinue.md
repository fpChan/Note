



## GPM 模型



- **Goroutine**

  每个 Goroutine 对应一个 G 结构体，G 存储 Goroutine 的运行堆栈、状态以及任务函数，可重用。G 并非执行体，每个 G 需要绑定到 P 才能被调度执行。G 任务创建后被放置在 P 本地队列或全局队列，等待工作线程调度 执行。

  ```go
  type stack struct { // go 运行的栈空间，一般指的都是虚拟内存划分区域，作为运行时的堆栈
  	lo uintptr        // lower 低位地址
  	hi uintptr        // high  高位地址
  }
  
  type g struct {
  	// It is ~0 on other goroutine stacks, to trigger a call to morestackc (and crash).
  	stack       stack   // offset known to runtime/cgo
  	stackguard0 uintptr // offset known to liblink 是 Go 栈空间的指针 stack.lo+StackGuard即具体指向位置
  	stackguard1 uintptr // offset known to liblink 是 C 栈空间的指针 stack.lo+StackGuard即具体指向位置
  
  	_panic       *_panic // innermost panic - offset known to liblink
  	_defer       *_defer // innermost defer
  	m            *m      // current m; offset known to arm liblink
  	sched        gobuf
  	syscallsp    uintptr        // if status==Gsyscall, syscallsp = sched.sp to use during gc
  	syscallpc    uintptr        // if status==Gsyscall, syscallpc = sched.pc to use during gc
  	stktopsp     uintptr        // expected sp at top of stack, to check in traceback
  	param        unsafe.Pointer // passed parameter on wakeup
  	atomicstatus uint32
  	stackLock    uint32 // sigprof/scang lock; TODO: fold in to atomicstatus
  	goid         int64
  	schedlink    guintptr
  	waitsince    int64      // approx time when the g become blocked
  	waitreason   waitReason // if status==Gwaiting
  
  	preempt       bool // preemption signal, duplicates stackguard0 = stackpreempt
  	preemptStop   bool // transition to _Gpreempted on preemption; otherwise, just deschedule
  	preemptShrink bool // shrink stack at synchronous safe point
  
  	// asyncSafePoint is set if g is stopped at an asynchronous
  	// safe point. This means there are frames on the stack
  	// without precise pointer information.
  	asyncSafePoint bool
  
  	paniconfault bool // panic (instead of crash) on unexpected fault address
  	gcscandone   bool // g has scanned stack; protected by _Gscan bit in status
  	throwsplit   bool // must not split stack
  	// activeStackChans indicates that there are unlocked channels
  	// pointing into this goroutine's stack. If true, stack
  	// copying needs to acquire channel locks to protect these
  	// areas of the stack.
  	activeStackChans bool
  	// parkingOnChan indicates that the goroutine is about to
  	// park on a chansend or chanrecv. Used to signal an unsafe point
  	// for stack shrinking. It's a boolean value, but is updated atomically.
  	parkingOnChan uint8
  
  	raceignore     int8     // ignore race detection events
  	sysblocktraced bool     // StartTrace has emitted EvGoInSyscall about this goroutine
  	sysexitticks   int64    // cputicks when syscall has returned (for tracing)
  	traceseq       uint64   // trace event sequencer
  	tracelastp     puintptr // last P emitted an event for this goroutine
  	lockedm        muintptr
  	sig            uint32
  	writebuf       []byte
  	sigcode0       uintptr
  	sigcode1       uintptr
  	sigpc          uintptr
  	gopc           uintptr         // pc of go statement that created this goroutine
  	ancestors      *[]ancestorInfo // ancestor information goroutine(s) that created this goroutine (only used if debug.tracebackancestors)
  	startpc        uintptr         // pc of goroutine function
  	racectx        uintptr
  	waiting        *sudog         // sudog structures this g is waiting on (that have a valid elem ptr); in lock order
  	cgoCtxt        []uintptr      // cgo traceback context
  	labels         unsafe.Pointer // profiler labels
  	timer          *timer         // cached timer for time.Sleep
  	selectDone     uint32         // are we participating in a select and did someone win the race?
  
  	// Per-G GC state
  
  	// gcAssistBytes is this G's GC assist credit in terms of
  	// bytes allocated. If this is positive, then the G has credit
  	// to allocate gcAssistBytes bytes without assisting. If this
  	// is negative, then the G must correct this by performing
  	// scan work. We track this in bytes to make it fast to update
  	// and check for debt in the malloc hot path. The assist ratio
  	// determines how this corresponds to scan work debt.
  	gcAssistBytes int64
  }
  ```

  

- **Processor**

  表示逻辑处理器， 对 G 来说，P 相当于 CPU 核，G 只有绑定到 P(在 P 的 local runq 中)才能被调度, 否则只能休眠，直到有空闲 P 时 被唤醒。线程独享所绑定的 P 资源，可在无锁状态下执行高效操作。

  对 M 来说，P 提供了相关的执行环境(Context)，如内存分配状态(mcache)，任务队列(G)等，P 的数量决定了系统内最大可并行的 G 的数量（前提：物理 CPU 核数 >= P 的数量），P 的数量由用户设置的 GOMAXPROCS 决定，但是不论 GOMAXPROCS 设置为多大，P 的数量最大为 256。

  ```go
  type p struct {
  	id          int32
  	status      uint32 // one of pidle/prunning/...
  	link        puintptr
  	schedtick   uint32     // incremented on every scheduler call
  	syscalltick uint32     // incremented on every system call
  	sysmontick  sysmontick // last tick observed by sysmon
  	m           muintptr   // back-link to associated m (nil if idle)
  	mcache      *mcache
  	pcache      pageCache
  	raceprocctx uintptr
  
  	deferpool    [5][]*_defer // pool of available defer structs of different sizes (see panic.go)
  	deferpoolbuf [5][32]*_defer
  
  	// Cache of goroutine ids, amortizes accesses to runtime·sched.goidgen.
  	goidcache    uint64
  	goidcacheend uint64
  
  	// Queue of runnable goroutines. Accessed without lock.
  	runqhead uint32
  	runqtail uint32
  	runq     [256]guintptr
  	// runnext, if non-nil, is a runnable G that was ready'd by
  	// the current G and should be run next instead of what's in
  	// runq if there's time remaining in the running G's time
  	// slice. It will inherit the time left in the current time
  	// slice. If a set of goroutines is locked in a
  	// communicate-and-wait pattern, this schedules that set as a
  	// unit and eliminates the (potentially large) scheduling
  	// latency that otherwise arises from adding the ready'd
  	// goroutines to the end of the run queue.
  	runnext guintptr
  
  	// Available G's (status == Gdead)
  	gFree struct {
  		gList
  		n int32
  	}
  
  	sudogcache []*sudog
  	sudogbuf   [128]*sudog
  
  	// Cache of mspan objects from the heap.
  	mspancache struct {
  		// We need an explicit length here because this field is used
  		// in allocation codepaths where write barriers are not allowed,
  		// and eliminating the write barrier/keeping it eliminated from
  		// slice updates is tricky, moreso than just managing the length
  		// ourselves.
  		len int
  		buf [128]*mspan
  	}
  
  	tracebuf traceBufPtr
  
  	// traceSweep indicates the sweep events should be traced.
  	// This is used to defer the sweep start event until a span
  	// has actually been swept.
  	traceSweep bool
  	// traceSwept and traceReclaimed track the number of bytes
  	// swept and reclaimed by sweeping in the current sweep loop.
  	traceSwept, traceReclaimed uintptr
  
  	palloc persistentAlloc // per-P to avoid mutex
  
  	_ uint32 // Alignment for atomic fields below
  
  	// The when field of the first entry on the timer heap.
  	// This is updated using atomic functions.
  	// This is 0 if the timer heap is empty.
  	timer0When uint64
  
  	// The earliest known nextwhen field of a timer with
  	// timerModifiedEarlier status. Because the timer may have been
  	// modified again, there need not be any timer with this value.
  	// This is updated using atomic functions.
  	// This is 0 if the value is unknown.
  	timerModifiedEarliest uint64
  
  	// Per-P GC state
  	gcAssistTime         int64 // Nanoseconds in assistAlloc
  	gcFractionalMarkTime int64 // Nanoseconds in fractional mark worker (atomic)
  
  	// gcMarkWorkerMode is the mode for the next mark worker to run in.
  	// That is, this is used to communicate with the worker goroutine
  	// selected for immediate execution by
  	// gcController.findRunnableGCWorker. When scheduling other goroutines,
  	// this field must be set to gcMarkWorkerNotWorker.
  	gcMarkWorkerMode gcMarkWorkerMode
  	// gcMarkWorkerStartTime is the nanotime() at which the most recent
  	// mark worker started.
  	gcMarkWorkerStartTime int64
  
  	// gcw is this P's GC work buffer cache. The work buffer is
  	// filled by write barriers, drained by mutator assists, and
  	// disposed on certain GC state transitions.
  	gcw gcWork
  
  	// wbBuf is this P's GC write barrier buffer.
  	//
  	// TODO: Consider caching this in the running G.
  	wbBuf wbBuf
  
  	runSafePointFn uint32 // if 1, run sched.safePointFn at next safe point
  
  	// statsSeq is a counter indicating whether this P is currently
  	// writing any stats. Its value is even when not, odd when it is.
  	statsSeq uint32
  
  	// Lock for timers. We normally access the timers while running
  	// on this P, but the scheduler can also do it from a different P.
  	timersLock mutex
  
  	// Actions to take at some time. This is used to implement the
  	// standard library's time package.
  	// Must hold timersLock to access.
  	timers []*timer
  
  	// Number of timers in P's heap.
  	// Modified using atomic instructions.
  	numTimers uint32
  
  	// Number of timerModifiedEarlier timers on P's heap.
  	// This should only be modified while holding timersLock,
  	// or while the timer status is in a transient state
  	// such as timerModifying.
  	adjustTimers uint32
  
  	// Number of timerDeleted timers in P's heap.
  	// Modified using atomic instructions.
  	deletedTimers uint32
  
  	// Race context used while executing timer functions.
  	timerRaceCtx uintptr
  
  	// preempt is set to indicate that this P should be enter the
  	// scheduler ASAP (regardless of what G is running on it).
  	preempt bool
  
  	pad cpu.CacheLinePad
  }
  ```

  

- **Machine**

  OS 线程抽象，代表着真正执行计算的资源，在绑定有效的 P 后，进入 schedule 循环；而 schedule 循环的机制大致是从 Global 队列、P 的 Local 队列以及 wait 队列中获取 G，切换到 G 的执行栈上并执行 G 的函数，调用 goexit 做清理工作并回到 M，如此反复。M 的数量是不定的，由 Go Runtime 调整，为了防止创建过多 OS 线程导致系统调度不过来，目前默认最大限制为 10000 个。

   M 通过修改寄存器，将执行栈指向 G 自带栈内存，并在此空间内分配堆栈帧，执行任务 函数。当需要中途切换时，只要将相关寄存器值保存回 G 空间即可维持状态，任何 M 都 可据此恢复执行。线程仅负责执行，不再持有状态，这是并发任务跨线程调度，实现多路 复用的根本所在。

  ```go
  type m struct {
  	g0      *g     // goroutine with scheduling stack
  	morebuf gobuf  // gobuf arg to morestack
  	divmod  uint32 // div/mod denominator for arm - known to liblink
  
  	// Fields not known to debuggers.
  	procid        uint64       // for debuggers, but offset not hard-coded
  	gsignal       *g           // signal-handling g
  	goSigStack    gsignalStack // Go-allocated signal handling stack
  	sigmask       sigset       // storage for saved signal mask
  	tls           [6]uintptr   // thread-local storage (for x86 extern register)
  	mstartfn      func()
  	curg          *g       // current running goroutine
  	caughtsig     guintptr // goroutine running during fatal signal
  	p             puintptr // attached p for executing go code (nil if not executing go code)
  	nextp         puintptr
  	oldp          puintptr // the p that was attached before executing a syscall
  	id            int64
  	mallocing     int32
  	throwing      int32
  	preemptoff    string // if != "", keep curg running on this m
  	locks         int32
  	dying         int32
  	profilehz     int32
  	spinning      bool // m is out of work and is actively looking for work
  	blocked       bool // m is blocked on a note
  	newSigstack   bool // minit on C thread called sigaltstack
  	printlock     int8
  	incgo         bool   // m is executing a cgo call
  	freeWait      uint32 // if == 0, safe to free g0 and delete m (atomic)
  	fastrand      [2]uint32
  	needextram    bool
  	traceback     uint8
  	ncgocall      uint64      // number of cgo calls in total
  	ncgo          int32       // number of cgo calls currently in progress
  	cgoCallersUse uint32      // if non-zero, cgoCallers in use temporarily
  	cgoCallers    *cgoCallers // cgo traceback if crashing in cgo call
  	doesPark      bool        // non-P running threads: sysmon and newmHandoff never use .park
  	park          note
  	alllink       *m // on allm
  	schedlink     muintptr
  	lockedg       guintptr
  	createstack   [32]uintptr // stack that created this thread.
  	lockedExt     uint32      // tracking for external LockOSThread
  	lockedInt     uint32      // tracking for internal lockOSThread
  	nextwaitm     muintptr    // next m waiting for lock
  	waitunlockf   func(*g, unsafe.Pointer) bool
  	waitlock      unsafe.Pointer
  	waittraceev   byte
  	waittraceskip int
  	startingtrace bool
  	syscalltick   uint32
  	freelink      *m // on sched.freem
  
  	// mFixup is used to synchronize OS related m state
  	// (credentials etc) use mutex to access. To avoid deadlocks
  	// an atomic.Load() of used being zero in mDoFixupFn()
  	// guarantees fn is nil.
  	mFixup struct {
  		lock mutex
  		used uint32
  		fn   func(bool) bool
  	}
  
  	// these are here because they are too large to be on the stack
  	// of low-level NOSPLIT functions.
  	libcall   libcall
  	libcallpc uintptr // for cpu profiler
  	libcallsp uintptr
  	libcallg  guintptr
  	syscall   libcall // stores syscall parameters on windows
  
  	vdsoSP uintptr // SP for traceback while in VDSO call (0 if not in call)
  	vdsoPC uintptr // PC for traceback while in VDSO call
  
  	// preemptGen counts the number of completed preemption
  	// signals. This is used to detect when a preemption is
  	// requested, but fails. Accessed atomically.
  	preemptGen uint32
  
  	// Whether this is a pending preemption signal on this M.
  	// Accessed atomically.
  	signalPending uint32
  
  	dlogPerM
  
  	mOS
  
  	// Up to 10 locks held by this m, maintained by the lock ranking code.
  	locksHeldLen int
  	locksHeld    [10]heldLockInfo
  }
  ```

  

## G-P-M 模型调度

Go 调度器工作时会维护两种用来保存 G 的任务队列：一种是一个 Global 任务队列，一种是每个 P 维护的 Local 任务队列。

当通过 `go` 关键字创建一个新的 goroutine 的时候，它会优先被放入 P 的本地队列。为了运行 goroutine，M 需要持有（绑定）一个 P，接着 M 会启动一个 OS 线程，循环从 P 的本地队列里取出一个 goroutine 并执行。当然还有上文提及的 `work-stealing` 调度算法：当 M 执行完了当前 P 的 Local 队列里的所有 G 后，P 也不会就这么在那躺尸啥都不干，它会先尝试从 Global 队列寻找 G 来执行，如果 Global 队列为空，它会随机挑选另外一个 P，从它的队列里中拿走一半的 G 到自己的队列中执行。







## Reference

[GMP 并发调度器深度解析之手撸一个高性能 goroutine pool](https://strikefreedom.top/high-performance-implementation-of-goroutine-pool)

