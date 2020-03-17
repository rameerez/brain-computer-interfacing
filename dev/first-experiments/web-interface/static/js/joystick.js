class JoystickElement {
  constructor(selector) {
    this.element = document.querySelector(selector);
    this.rect = this.calculateRect();
    this.current = this.original;

    // Recalculate the rect on resizing
    window.onresize = () => {
      this.rect = this.calculateRect();
    };
  }

  get original() {
    return {
      vector: {
        x: 0,
        y: 0
      },

      angle: 0,
      percentage: 0
    };
  }

  calculateRect() {
    let rect = this.element.getBoundingClientRect();

    return Object.assign(rect, {
      center: {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2
      },

      radius: rect.width / 2 // Improve this
    });
  }
}

class JoystickShaft extends JoystickElement {
  clamp(x, y, boundary) {
    // Trigonometry time!
    // - Who says what you learn in school won't become useful :D
    let diff = {
      x: x - this.rect.center.x,
      y: y - this.rect.center.y
    };

    // Get the distance between the cursor and the center
    let distance = Math.sqrt(Math.pow(diff.x, 2) + Math.pow(diff.y, 2));

    // Get the angle of the line
    let angle = Math.atan2(diff.x, diff.y);
    // Convert into degrees!
    this.current.angle = 180 - (angle * 180) / Math.PI;

    // If the cursor is distance from the center is
    // less than the boundary, then return the diff
    //
    // Note: Boundary = radius
    if (distance < boundary) {
      this.current.percentage = (distance / boundary) * 100;
      return (this.current.vector = diff);
    }

    // If it's a longer distance, clamp it!
    this.current.percentage = 100;

    return (this.current.vector = {
      x: Math.sin(angle) * boundary,
      y: Math.cos(angle) * boundary
    });
  }

  move(from, to, duration, callback) {
    Velocity(
      this.element,
      {
        translateX: [to.x, from.x],
        translateY: [to.y, from.y],
        translateZ: 0
      },

      {
        duration: duration,
        queue: false,
        complete() {
          if (typeof callback === "function") {
            callback();
          }
        }
      }
    );
  }
}

class Joystick {
  constructor(base, shaft) {
    this.state = "inactive";
    this.base = new JoystickElement(base);
    this.shaft = new JoystickShaft(shaft);
    this.boundary = this.base.rect.radius * 0.75;

    this.onactivate = function() {};
    this.ondeactivate = function() {};
    this.ondrag = function() {};

    this.activate = this.activate.bind(this);
    this.deactivate = this.deactivate.bind(this);
    this.drag = this.drag.bind(this);
  }

  static get ANIMATION_TIME() {
    return 100;
  }

  attachEvents() {
    this.activate();
    // this.base.element.addEventListener("pointerdown", this.activate, false);
    // document.addEventListener("pointerup", this.deactivate, false);
    document.addEventListener("pointermove", this.drag, false);

    return this;
  }

  detachEvents() {
    this.base.element.removeEventListener("pointerdown", this.activate, false);
    document.removeEventListener("pointerup", this.deactivate, false);
    document.removeEventListener("pointermove", this.drag, false);

    this.deactivate();

    return this;
  }

  activate() {
    this.state = "active";
    this.base.element.classList.add("active");

    if (typeof this.onactivate === "function") {
      this.onactivate();
    }

    return this;
  }

  deactivate() {
    this.state = "inactive";
    this.base.element.classList.remove("active");

    this.shaft.move(
      this.shaft.current.vector,
      this.shaft.original.vector,
      this.constructor.ANIMATION_TIME,
      () => {
        this.shaft.element.removeAttribute("style");
        this.shaft.current = this.shaft.original;

        if (typeof this.ondeactivate === "function") {
          this.ondeactivate();
        }
      }
    );

    return this;
  }

  drag(e) {
    // console.log(e);
    if (this.state !== "active") {
      return this;
    }

    this.shaft.move(
      this.shaft.original.vector,
      this.shaft.clamp(e.clientX, e.clientY, this.boundary),
      0,
      () => {
        if (typeof this.ondrag === "function") {
          this.ondrag();
        }
      }
    );

    return this;
  }
}

// Setup the Joystick
const joystick = new Joystick(".joystick-base", ".joystick-shaft");

// Attach the events for the joystick
// Can also detach events with the detachEvents function
joystick.attachEvents();

// Lets animate the background colour around using hsl to show the degree of control this has!
// Puns are funny.
joystick.ondeactivate = function() {
  document.body.removeAttribute("style");
};

joystick.ondrag = function() {
  var angle = this.shaft.current.angle;
  var alpha = this.shaft.current.percentage / 100;
  if (angle >= 0 && angle < 180) {
    document.body.style.background = `rgba(127, 219, 255, ${alpha})`;
  } else {
    document.body.style.background = `rgba(255, 65, 54, ${alpha})`;
  }
  // document.body.style.background = `hsl(${this.shaft.current.angle}, ${this.shaft.current.percentage}%, 50%)`;
};
