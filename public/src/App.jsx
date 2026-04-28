const { useState, useEffect, useRef } = React;

const SERVER_URI = process.env.REACT_APP_SERVER_URI || 'http://localhost:5000';

const years = Array.from({ length: 2023 - 1980 + 1 }, (_, i) => 1980 + i);

const defaultMakes = ['Acura', 'Audi', 'BMW', 'Buick', 'Cadillac', 'Chevrolet', 'Chrysler', 'Dodge', 'Ferrari', 'Ford', 'GMC', 'Honda', 'Hyundai', 'Infiniti', 'Jaguar', 'Jeep', 'Kia', 'Lamborghini', 'Lexus', 'Lincoln', 'Maserati', 'Mazda', 'Mercedes-Benz', 'Mini', 'Mitsubishi', 'Nissan', 'Porsche', 'Ram', 'Rolls-Royce', 'Subaru', 'Tesla', 'Toyota', 'Volkswagen', 'Volvo'];
const defaultModels = ['911', 'A4', 'A6', 'Accord', 'Altima', 'Beetle', 'Boxster', 'Camaro', 'Camry', 'Cayenne', 'Challenger', 'Charger', 'Cherokee', 'Civic', 'Corolla', 'Corvette', 'CR-V', 'Cruze', 'Dart', 'Durango', 'E-Class', 'Edge', 'Equinox', 'Escape', 'Explorer', 'F-150', 'F-250', 'Fiesta', 'Focus', 'Forester', 'Fortwo', 'Frontier', 'Fusion', 'G-Class', 'GLA', 'GLC', 'GLE', 'Grand Cherokee', 'Highlander', 'HR-V', 'Hummer', 'Ilx', 'Impala', 'IS', 'Jetta', 'Journey', 'Kona', 'LaFerrari', 'Legacy', 'Levante', 'Lexus IS', 'Malibu', 'Maxima', 'Mazda3', 'Mazda6', 'MDX', 'Model S', 'Model X', 'Mustang', 'Navigator', 'NV', 'Odyssey', 'Optima', 'Outback', 'Outlander', 'Pacifica', 'Pilot', 'Prius', 'Q5', 'Q7', 'Quattroporte', 'Ranger', 'RAV4', 'Renegade', 'Ridgeline', 'Rio', 'RX', 'Santa Fe', 'Scion', 'Sedona', 'Sentra', 'Sierra', 'Silverado', 'Sonata', 'Sorento', 'Soul', 'Spark', 'Spirior', 'Sportage', 'SRX', 'Stinger', 'Suburban', 'Tahoe', 'Taurus', 'Terrain', 'Tiguan', 'Titan', 'Touareg', 'Trailblazer', 'Traverse', 'Trax', 'TT', 'Tucson', 'Tundra', 'Uplander', 'URUS', 'Verano', 'Versa', 'Vitara', 'Wrangler', 'X1', 'X3', 'X5', 'X6', 'XC60', 'XC90', 'Yukon'];
const defaultEngines = ['P9', 'P8', 'V1', 'I6', 'Electric', 'I2', 'H6', 'I3', 'I5', 'Flat-2', 'I4', 'Flat-4', 'R6', 'H4', 'V6', 'W8', 'V2', 'Flat-6', 'V8'];
const titleStatuses = ['Clean', 'Salvage', 'Other'];
const driveTrains = ['Rear-wheel drive', '4WD/AWD', 'Front-wheel drive'];
const bodyStyles = ['SUV/Crossover', 'Hatchback', 'Convertible', 'Van/Minivan', 'Sedan', 'Wagon', 'Truck', 'Coupe'];
const reserves = ['Reserve', 'No Reserve'];
const transmissions = ['Manual', 'Automatic'];
const modelPaths = ['GradientBoostingRegressor', 'RandomForestRegressor', 'XGBRegressor'];

function Header() {
    return (
        <div className="header-section">
            <div className="container">
                <div className="row align-items-center">
                    <div className="col-md-6">
                        <h1 style={{ textAlign: 'center' }}>How Much is Your Collector Car Worth?</h1>
                        <p className="text-center">Use our API and predict a sale price for your vehicle!</p>
                    </div>
                    <div className="col-md-6 text-center">
                        <img 
                            src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTe1SBdlXWtJ96-zcUnN05YMaumzpJ-q2ei-A&usqp=CAU" 
                            alt="Car" 
                            style={{ maxWidth: '300px', borderRadius: '8px' }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

function Navigation({ activeTab, setActiveTab }) {
    return (
        <ul className="nav nav-tabs justify-content-center mb-4">
            <li className="nav-item">
                <button 
                    className={`nav-link ${activeTab === 'Predict' ? 'active' : ''}`}
                    onClick={() => setActiveTab('Predict')}
                >
                    Predict
                </button>
            </li>
            <li className="nav-item">
                <button 
                    className={`nav-link ${activeTab === 'FAQ' ? 'active' : ''}`}
                    onClick={() => setActiveTab('FAQ')}
                >
                    FAQ
                </button>
            </li>
            <li className="nav-item">
                <button 
                    className={`nav-link ${activeTab === 'API' ? 'active' : ''}`}
                    onClick={() => setActiveTab('API')}
                >
                    API
                </button>
            </li>
        </ul>
    );
}

function PredictForm() {
    const [formData, setFormData] = useState({
        make: 'Acura',
        model: 'ILX',
        year: 2022,
        engine: 'I4',
        title_status: 'Clean',
        drivetrain: 'Front-wheel drive',
        body_style: 'Sedan',
        y_n_reserve: 'No Reserve',
        transmission: 'Automatic',
        vin: '',
        mileage: '',
        tree_model: 'GradientBoostingRegressor'
    });
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const chartRef = useRef(null);
    const chartInstanceRef = useRef(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setResult(null);

        try {
            const payload = {
                make: formData.make,
                model: formData.model,
                year: parseInt(formData.year),
                engine: formData.engine,
                title_status: formData.title_status,
                drivetrain: formData.drivetrain,
                body_style: formData.body_style,
                y_n_reserve: formData.y_n_reserve,
                transmission: formData.transmission,
                mileage: formData.mileage ? parseFloat(formData.mileage) : 0,
                tree_model: formData.tree_model
            };

            if (formData.vin) {
                payload.vin = formData.vin;
            }

            const response = await fetch(`${SERVER_URI}/predict_streamlit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('Failed to make prediction');

            const data = await response.json();
            setResult({
                predictedPrice: data[0][0],
                shaps: data[1]
            });
        } catch (err) {
            setError('Failed to make prediction. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (result && result.shaps && chartRef.current) {
            if (chartInstanceRef.current) {
                chartInstanceRef.current.destroy();
            }

            const labels = Object.keys(result.shaps);
            const values = Object.values(result.shaps);

            chartInstanceRef.current = new Chart(chartRef.current, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Dollar Contribution',
                        data: values,
                        backgroundColor: values.map(v => v >= 0 ? 'rgba(40, 167, 69, 0.7)' : 'rgba(220, 53, 69, 0.7)'),
                        borderColor: values.map(v => v >= 0 ? 'rgba(40, 167, 69, 1)' : 'rgba(220, 53, 69, 1)'),
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                        title: { display: true, text: 'Dollar Contribution of Each Feature to the Predicted Sale Price' }
                    },
                    scales: {
                        x: { title: { display: true, text: 'Dollars' } }
                    }
                }
            });
        }
    }, [result]);

    return (
        <div className="container">
            <div className="form-card">
                <p className="mb-4">
                    CarsAndBids.com is a new auction website for collector cars from the 80s until now. With a rich history of auctions, 
                    we wanted to learn if we could predict which cars would be good deals on the site by using features of the vehicle 
                    like Make, Model, Year, Engine (etc.) as well as car market data on the vehicle and general market data, we fit a 
                    gradient boosted decision tree to predict the selling price of the car.
                </p>

                <form onSubmit={handleSubmit}>
                    <div className="row">
                        <div className="col-md-3 mb-3">
                            <label className="form-label">Make</label>
                            <select className="form-select" name="make" value={formData.make} onChange={handleChange}>
                                {defaultMakes.map(m => <option key={m} value={m}>{m}</option>)}
                            </select>
                        </div>
                        <div className="col-md-3 mb-3">
                            <label className="form-label">Model</label>
                            <select className="form-select" name="model" value={formData.model} onChange={handleChange}>
                                {defaultModels.map(m => <option key={m} value={m}>{m}</option>)}
                            </select>
                        </div>
                        <div className="col-md-3 mb-3">
                            <label className="form-label">Year</label>
                            <select className="form-select" name="year" value={formData.year} onChange={handleChange}>
                                {years.map(y => <option key={y} value={y}>{y}</option>)}
                            </select>
                        </div>
                        <div className="col-md-3 mb-3">
                            <label className="form-label">Engine</label>
                            <select className="form-select" name="engine" value={formData.engine} onChange={handleChange}>
                                {defaultEngines.map(e => <option key={e} value={e}>{e}</option>)}
                            </select>
                        </div>
                    </div>

                    <div className="row">
                        <div className="col-md-3 mb-3">
                            <label className="form-label">Title Status</label>
                            <select className="form-select" name="title_status" value={formData.title_status} onChange={handleChange}>
                                {titleStatuses.map(t => <option key={t} value={t}>{t}</option>)}
                            </select>
                        </div>
                        <div className="col-md-3 mb-3">
                            <label className="form-label">Drivetrain</label>
                            <select className="form-select" name="drivetrain" value={formData.drivetrain} onChange={handleChange}>
                                {driveTrains.map(d => <option key={d} value={d}>{d}</option>)}
                            </select>
                        </div>
                        <div className="col-md-3 mb-3">
                            <label className="form-label">Body Style</label>
                            <select className="form-select" name="body_style" value={formData.body_style} onChange={handleChange}>
                                {bodyStyles.map(b => <option key={b} value={b}>{b}</option>)}
                            </select>
                        </div>
                        <div className="col-md-3 mb-3">
                            <label className="form-label">Reserve</label>
                            <select className="form-select" name="y_n_reserve" value={formData.y_n_reserve} onChange={handleChange}>
                                {reserves.map(r => <option key={r} value={r}>{r}</option>)}
                            </select>
                        </div>
                    </div>

                    <div className="row">
                        <div className="col-md-3 mb-3">
                            <label className="form-label">Transmission</label>
                            <select className="form-select" name="transmission" value={formData.transmission} onChange={handleChange}>
                                {transmissions.map(t => <option key={t} value={t}>{t}</option>)}
                            </select>
                        </div>
                        <div className="col-md-3 mb-3">
                            <label className="form-label">VIN (Optional)</label>
                            <input type="text" className="form-control" name="vin" value={formData.vin} onChange={handleChange} placeholder="Enter VIN" />
                        </div>
                        <div className="col-md-3 mb-3">
                            <label className="form-label">Mileage</label>
                            <input type="number" className="form-control" name="mileage" value={formData.mileage} onChange={handleChange} placeholder="Enter mileage" />
                        </div>
                        <div className="col-md-3 mb-3">
                            <label className="form-label">ML Model</label>
                            <select className="form-select" name="tree_model" value={formData.tree_model} onChange={handleChange}>
                                {modelPaths.map(m => <option key={m} value={m}>{m}</option>)}
                            </select>
                        </div>
                    </div>

                    <button type="submit" className="submit-btn" disabled={loading}>
                        {loading ? 'Running Prediction...' : 'Submit'}
                    </button>
                </form>
            </div>

            {error && <div className="alert alert-danger">{error}</div>}

            {result && (
                <div className="result-card">
                    <h5 className="mb-3">Dollar Contribution of Each Feature to the Predicted Sale Price</h5>
                    <canvas ref={chartRef} style={{ maxHeight: '400px' }}></canvas>
                    <div className="text-center mt-4">
                        <h2 className="price-display">
                            Predicted Price on CarsAndBids.com: ${Math.round(result.predictedPrice).toLocaleString()}
                        </h2>
                    </div>
                </div>
            )}
        </div>
    );
}

function FAQ() {
    const faqs = [
        {
            question: "What data is used for the model?",
            answer: "Data is collected from CarsandBids.com. Cars and Bids is an online enthusiast car sales platform created by the automotive Youtuber Doug DeMuro. Most listings on the platform are sold in auction format. Listings are also cross referenced against market data for the vehicle via VinAudit.com for additional data"
        },
        {
            question: "What model is being used to predict sale price?",
            answer: "We are using a Gradient Boosted Regression Tree to predict sale price. If the VIN is provided, we gather market data about the vehicle to include as predictors. If not, we use only features from the vehicle (two separate models)."
        },
        {
            question: "How was the data collected?",
            answer: "All of the past listings from CarsAndBids.com were collected using webscraping via selenium, which collects data nightly. We collected estimated market price for each vehicle from VinAudit.com as well as overall market conditions at the time of sale via Yahoo Finance"
        },
        {
            question: "Can I use this site commercially?",
            answer: "This site is not intended to be used commercially and should not be used commercially"
        },
        {
            question: "Is the car price prediction sound financial advice?",
            answer: "No. This is a purely academic exercise; use the model output at your own discretion"
        }
    ];

    return (
        <div className="container">
            {faqs.map((faq, index) => (
                <div className="faq-item" key={index}>
                    <h5>{faq.question}</h5>
                    <p className="mb-0">{faq.answer}</p>
                </div>
            ))}
        </div>
    );
}

function APIDocumentation() {
    const apiParams = [
        { name: 'make', required: 'yes', dataType: 'string', acceptedValues: 'Any brand of auto manufacturer.' },
        { name: 'model', required: 'yes', dataType: 'string', acceptedValues: 'Any model from an auto manufacturer.' },
        { name: 'mileage', required: 'yes', dataType: 'float', acceptedValues: 'Any positive number (without commas)' },
        { name: 'title_status', required: 'yes', dataType: 'string', acceptedValues: 'Clean, Salvage, Other' },
        { name: 'engine', required: 'yes', dataType: 'string', acceptedValues: 'P9, P8, V1, I6, Electric, I2, H6, I3, I5, Flat-2, I4, Flat-4, R6, H4, V6, W8, V2, Flat-6, V8' },
        { name: 'body_style', required: 'yes', dataType: 'string', acceptedValues: 'SUV/Crossover, Hatchback, Convertible, Van/Minivan, Sedan, Wagon, Truck, Coupe' },
        { name: 'y_n_reserve', required: 'yes', dataType: 'string', acceptedValues: 'Reserve, No Reserve' },
        { name: 'year', required: 'yes', dataType: 'int', acceptedValues: 'Any year from 1980 - present' },
        { name: 'drivetrain', required: 'yes', dataType: 'string', acceptedValues: 'Rear-wheel drive, 4WD/AWD, Front-wheel drive' },
        { name: 'transmission', required: 'yes', dataType: 'string', acceptedValues: 'Manual, Automatic' },
        { name: 'vin', required: 'no', dataType: 'string', acceptedValues: 'Any valid VIN number' }
    ];

    return (
        <div className="container">
            <div className="form-card">
                <h4>Our API is free to use and available via a POST request to http://api.carcollectorpricing.com/predict</h4>
                <p>The post request must include the following parameters:</p>

                <div className="table-responsive">
                    <table className="table table-striped">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Required</th>
                                <th>Data Type</th>
                                <th>Accepted Values</th>
                            </tr>
                        </thead>
                        <tbody>
                            {apiParams.map((param, index) => (
                                <tr key={index}>
                                    <td>{param.name}</td>
                                    <td>{param.required}</td>
                                    <td>{param.dataType}</td>
                                    <td>{param.acceptedValues}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <h5 className="mt-4">Example:</h5>
                <pre className="bg-light p-3 rounded">
{`curl -d '{"make": "Acura","model": "Cayenne","mileage": "500.0","title_status": "Clean" , "engine":"3.6L V6","drivetrain": "4WD/AWD","transmission" :"Automatic","body_style":" SUV/Crossover", "y_n_reserve":" No Reserve","year":"2022.0"}' -X POST  http://api.carcollectorpricing.com/predict`}
                </pre>
            </div>
        </div>
    );
}

function Footer() {
    return (
        <footer className="text-center mt-5 py-4" style={{ backgroundColor: '#343a40', color: 'white' }}>
            <p className="mb-1">
                <a href="https://github.com/AdamLang96/CarSalesModel" target="_blank" rel="noopener noreferrer" style={{ color: 'white' }}>
                    Developed by Adam Lang [Github Repo]
                </a>
            </p>
            <p className="mb-0">Contact me at adamglang96@gmail.com</p>
        </footer>
    );
}

function App() {
    const [activeTab, setActiveTab] = useState('Predict');

    return (
        <div>
            <Header />
            <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />
            
            {activeTab === 'Predict' && <PredictForm />}
            {activeTab === 'FAQ' && <FAQ />}
            {activeTab === 'API' && <APIDocumentation />}
            
            <Footer />
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);